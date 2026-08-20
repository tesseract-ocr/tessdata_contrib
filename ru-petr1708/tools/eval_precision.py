#!/usr/bin/env python3
"""Score candidate models against orusd on real pre-reform pages.

The synthetic eval split cannot answer the question this project turns on.
Fita is о with a crossbar, and a crossbar survives rendering; it does not
survive a library scan. A model can read every rendered ѳ perfectly and still
be worthless on the corpus, and -- far more dangerous -- a model can gain fita
by learning to guess it, which shows up on rendered text as a win and on real
pages as damage to о.

So the decision is made here, on scanned pages with hand-verified ground truth,
and the number that decides it is not fita recall. Over the dictionary о
outnumbers ѳ by roughly 860:1, so a model that trades one point of о precision
for ten points of fita recall loses on every page it will ever see.

What is measured, per model, per page:

  CER / WER          against the transcription, on normalised text
  CER excluding      the same with ѳѲѵѴ positions dropped, which answers
    the new letters  "did the base competence survive the fine-tune"
  per-letter         precision and recall for each of ѳ Ѳ ѵ Ѵ
  о damage           true о read as ѳ -- the error that costs the most
  confusions         what the model actually put where the letter belonged

Alignment is an exact Levenshtein backtrace, not a heuristic diff. The counts
below are substitution pairs read off the minimal edit path, so "о read as ѳ"
means that and not "appeared near".

Usage:
  tools/eval_precision.py --page IMG GT [--page IMG GT ...] \
                          --model NAME [--model NAME ...] [--baseline orusd]
"""

import argparse
import collections
import csv
import io
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEW = 'ѳѲѵѴ'
DIAG, DEL, INS = 0, 1, 2


def stock_tessdata():
    """Where the tesseract build keeps its own traineddata and configs."""
    out = subprocess.run(['tesseract', '--list-langs'],
                         capture_output=True, text=True).stdout \
        + subprocess.run(['tesseract', '--list-langs'],
                         capture_output=True, text=True).stderr
    m = re.search(r'"(.*?)"', out)
    if not m:
        sys.exit('cannot locate stock tessdata directory')
    return pathlib.Path(m.group(1))


def align(a, b):
    """Minimal edit path from a to b as a list of (op, ai, bi).

    op is '=' equal, 'X' substitution, '-' deletion from a, '+' insertion of b.

    a and b are any sequences of hashable items -- this is called both on
    character strings and on word lists, so the items are interned to integers
    rather than assumed to be characters.

    The row update is vectorised. Deletion and substitution only look at the
    previous row, so they fall out directly; insertion is the awkward one,
    since cur[j] depends on cur[j-1]. Writing the recurrence out,

        cur[j] = min over k <= j of (tmp[k] + (j - k))

    which is a running minimum of tmp[k] - k, offset by j -- so
    minimum.accumulate does it in one pass with no Python loop over columns.
    """
    n, m = len(a), len(b)
    code = {}
    for item in a:
        code.setdefault(item, len(code))
    for item in b:
        code.setdefault(item, len(code))
    acodes = [code[x] for x in a]
    bcodes = np.fromiter((code[x] for x in b), dtype=np.int32, count=m)

    back = np.zeros((n + 1, m + 1), dtype=np.uint8)
    back[0, 1:] = INS
    back[1:, 0] = DEL

    prev = np.arange(m + 1, dtype=np.int32)
    cols = np.arange(m + 1, dtype=np.int32)

    for i in range(1, n + 1):
        cost = (bcodes != acodes[i - 1]).astype(np.int32)
        diag = prev[:-1] + cost
        up = prev[1:] + 1
        tmp = np.empty(m + 1, dtype=np.int32)
        tmp[0] = i
        tmp[1:] = np.minimum(diag, up)
        src = np.where(diag <= up, DIAG, DEL).astype(np.uint8)

        cur = np.minimum.accumulate(tmp - cols) + cols
        back[i, 0] = DEL
        # cur[j] < tmp[j] can only have come from the left.
        back[i, 1:] = np.where(cur[1:] < tmp[1:], INS, src)
        prev = cur

    ops = []
    i, j = n, m
    while i > 0 or j > 0:
        step = back[i, j]
        if step == DIAG:
            ops.append(('=' if a[i - 1] == b[j - 1] else 'X', i - 1, j - 1))
            i -= 1
            j -= 1
        elif step == DEL:
            ops.append(('-', i - 1, None))
            i -= 1
        else:
            ops.append(('+', None, j - 1))
            j -= 1
    ops.reverse()
    return ops


def normalise(text):
    """Whitespace is not a thing either transcription or OCR agrees on."""
    return re.sub(r'\s+', ' ', text).strip()


def reading_order(tsv_text):
    """Page text in reading order, de-hyphenated.

    Tesseract's own text output cannot be used directly on these pages. Dahl
    sets each letter's section as a headed two-column block, and two sections
    share this page; tesseract sees two full-height columns instead and emits
    left-column-Ѳ, left-column-Ѵ, right-column-Ѳ, right-column-Ѵ. Every
    character is present and correct, but the order is wrong, and an edit
    distance against the transcription then reports about 50% error for a page
    that was read rather well. That would have buried the effect being measured
    under an artefact of layout analysis.

    The block boxes are clean, so the order is recovered geometrically: sweep
    blocks top to bottom, group into bands of vertically overlapping blocks,
    and read each band left to right. On this layout that yields
    header, Ѳ-left, Ѳ-right, header, Ѵ-left, Ѵ-right, footer -- the
    transcription's order.

    Line-final hyphens are joined to the following word. They are an artefact
    of justification and the transcription does not carry them; a real
    compound hyphen sits mid-line and is left alone.
    """
    rows = list(csv.DictReader(io.StringIO(tsv_text), delimiter='\t',
                               quoting=csv.QUOTE_NONE))
    blocks = {}
    for r in rows:
        if int(r['level']) != 5 or not (r['text'] or '').strip():
            continue
        key = int(r['block_num'])
        left, top = int(r['left']), int(r['top'])
        right, bottom = left + int(r['width']), top + int(r['height'])
        b = blocks.setdefault(key, {'box': [left, top, right, bottom],
                                    'lines': collections.OrderedDict()})
        box = b['box']
        box[0], box[1] = min(box[0], left), min(box[1], top)
        box[2], box[3] = max(box[2], right), max(box[3], bottom)
        lkey = (int(r['par_num']), int(r['line_num']))
        b['lines'].setdefault(lkey, []).append(r['text'])

    ordered = sorted(blocks.values(), key=lambda b: b['box'][1])
    bands = []
    for b in ordered:
        if bands and b['box'][1] < bands[-1]['bottom']:
            bands[-1]['blocks'].append(b)
            bands[-1]['bottom'] = max(bands[-1]['bottom'], b['box'][3])
        else:
            bands.append({'bottom': b['box'][3], 'blocks': [b]})

    lines = []
    for band in bands:
        for b in sorted(band['blocks'], key=lambda b: b['box'][0]):
            lines.extend(' '.join(w) for w in b['lines'].values())

    out = []
    for line in lines:
        if out and out[-1].endswith('-'):
            out[-1] = out[-1][:-1] + line.lstrip()
        else:
            out.append(line)
    return '\n'.join(out)


def run_ocr(image, lang, tessdata, psm='3', upscale=2):
    """OCR one page, returning text in reading order.

    The scans run about 170 dpi, which is below what tesseract's line
    normaliser prefers; upscaling before recognition is the ordinary remedy
    and is applied identically to every model, so it cannot favour one.
    """
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / 'page.png'
        im = Image.open(image)
        if upscale != 1:
            im = im.resize((im.width * upscale, im.height * upscale),
                           Image.LANCZOS)
        im.save(src, dpi=(300, 300))
        base = pathlib.Path(td) / 'out'
        env = dict(os.environ, TESSDATA_PREFIX=str(tessdata))
        r = subprocess.run(
            ['tesseract', str(src), str(base), '-l', lang, '--psm', psm,
             'tsv'],
            capture_output=True, text=True, env=env)
        if r.returncode != 0:
            sys.exit(f'tesseract failed on {image} with -l {lang}:\n{r.stderr}')
        return reading_order(
            base.with_suffix('.tsv').read_text(encoding='utf-8'))


def score(gt, ocr):
    """Metrics for one page, one model."""
    ops = align(gt, ocr)

    edits = sum(1 for op, _, _ in ops if op != '=')
    # Same edit path, but any step touching one of the four new letters on
    # either side is dropped. What is left is the model's competence on the
    # 133 characters it already had, which the fine-tune must not have spent.
    base_edits = 0
    base_len = 0
    for op, ai, bi in ops:
        g = gt[ai] if ai is not None else None
        o = ocr[bi] if bi is not None else None
        if (g is not None and g in NEW) or (o is not None and o in NEW):
            continue
        if g is not None:
            base_len += 1
        if op != '=':
            base_edits += 1

    gt_words, ocr_words = gt.split(), ocr.split()
    wops = align(gt_words, ocr_words)
    werr = sum(1 for op, _, _ in wops if op != '=')

    # Substitution and deletion detail, keyed on the ground-truth character.
    got = collections.defaultdict(collections.Counter)   # gt char -> ocr char
    emitted = collections.defaultdict(collections.Counter)  # ocr char -> gt char
    for op, ai, bi in ops:
        g = gt[ai] if ai is not None else None
        o = ocr[bi] if bi is not None else None
        if g is not None:
            got[g][o if o is not None else ''] += 1
        if o is not None:
            emitted[o][g if g is not None else ''] += 1

    letters = {}
    for ch in NEW + 'о':
        n_gt = sum(got[ch].values())
        n_ocr = sum(emitted[ch].values())
        hit = got[ch][ch]
        letters[ch] = {
            'gt': n_gt,
            'ocr': n_ocr,
            'hit': hit,
            'recall': hit / n_gt if n_gt else None,
            'precision': hit / n_ocr if n_ocr else None,
            'read_as': got[ch],
            'came_from': emitted[ch],
        }

    return {
        'cer': edits / len(gt),
        'wer': werr / len(gt_words),
        'base_cer': base_edits / base_len if base_len else 0.0,
        'letters': letters,
        'chars': len(gt),
    }


def pct(x):
    return '   -  ' if x is None else f'{x * 100:6.2f}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--page', nargs=2, action='append', metavar=('IMG', 'GT'),
                    required=True)
    ap.add_argument('--model', action='append', required=True,
                    help='language name resolvable in the assembled tessdata')
    ap.add_argument('--baseline', default='orusd')
    ap.add_argument('--models-dir', default=str(ROOT / 'work/models'))
    ap.add_argument('--psm', default='3')
    ap.add_argument('--upscale', type=int, default=2)
    ap.add_argument('--verbose', action='store_true',
                    help='print the confusion detail for the new letters')
    args = ap.parse_args()

    # One tessdata directory holding every model under test plus the stock
    # configs, so each run differs only in -l.
    stock = stock_tessdata()
    td = ROOT / 'work/evaldata'
    if td.exists():
        shutil.rmtree(td)
    td.mkdir(parents=True)
    (td / 'configs').symlink_to(stock / 'configs')
    wanted = [args.baseline] + args.model
    for name in wanted:
        dst = td / f'{name}.traineddata'
        if dst.exists():
            continue
        for cand in (pathlib.Path(args.models_dir) / f'{name}.traineddata',
                     stock / f'{name}.traineddata'):
            if cand.exists():
                dst.symlink_to(cand)
                break
        else:
            sys.exit(f'no traineddata for {name!r} in {args.models_dir} '
                     f'or {stock}')

    for image, gtfile in args.page:
        gt = normalise(pathlib.Path(gtfile).read_text(encoding='utf-8'))
        print(f'\n=== {pathlib.Path(image).name}  '
              f'({len(gt)} chars, gt {gtfile}) ===')
        n_new = sum(gt.count(c) for c in NEW)
        print(f'    ground truth carries {n_new} new-letter instances '
              + ' '.join(f'{c}x{gt.count(c)}' for c in NEW if gt.count(c)))
        print()
        print(f'    {"model":28} {"CER":>6} {"WER":>6} {"CER-":>6} '
              + ' '.join(f'{c + " P":>6} {c + " R":>6}' for c in NEW)
              + f' {"о->ѳ":>6}')

        rows = {}
        for name in wanted:
            ocr = normalise(run_ocr(image, name, td, args.psm, args.upscale))
            s = score(gt, ocr)
            rows[name] = (s, ocr)
            o_as_fita = s['letters']['о']['read_as']['ѳ'] \
                + s['letters']['о']['read_as']['Ѳ']
            print(f'    {name:28} {pct(s["cer"])} {pct(s["wer"])} '
                  f'{pct(s["base_cer"])} '
                  + ' '.join(f'{pct(s["letters"][c]["precision"])} '
                             f'{pct(s["letters"][c]["recall"])}' for c in NEW)
                  + f' {o_as_fita:6d}')

        base = rows[args.baseline][0]
        print()
        for name in args.model:
            s = rows[name][0]
            d_cer = (s['cer'] - base['cer']) * 100
            d_base = (s['base_cer'] - base['base_cer']) * 100
            got_new = sum(s['letters'][c]['hit'] for c in NEW)
            spur = sum(s['letters'][c]['ocr'] - s['letters'][c]['hit']
                       for c in NEW)
            print(f'    {name:28} dCER {d_cer:+6.2f}  dCER- {d_base:+6.2f}  '
                  f'new letters correct {got_new:3d}/{n_new}  spurious {spur:3d}')

        if args.verbose:
            for name in wanted:
                s = rows[name][0]
                print(f'\n    -- {name} --')
                for c in NEW:
                    L = s['letters'][c]
                    if L['gt'] or L['ocr']:
                        print(f'       {c} gt {L["gt"]:3d} read as: '
                              + ' '.join(f'{k or "(del)"}x{v}'
                                         for k, v in L['read_as'].most_common()))
                        print(f'       {c} ocr{L["ocr"]:3d} came from: '
                              + ' '.join(f'{k or "(ins)"}x{v}'
                                         for k, v in L['came_from'].most_common()))


if __name__ == '__main__':
    main()
