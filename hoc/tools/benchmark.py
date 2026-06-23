#!/usr/bin/env python3
"""
benchmark.py — Santali OCR accuracy comparison.

Compares sat_v1 (our trained LSTM) vs sat_indicocr (indic-ocr legacy model).
Computes CER, WER, and Space Recall on test images.

Usage:
  python3 tools/benchmark.py [--test-dir DIR] [--psm PSM]

Default test dir: test-images/
"""

import sys, re, subprocess, argparse
from pathlib import Path
from itertools import zip_longest

IMAGE_EXTS = {'.png', '.ppm', '.jpg', '.jpeg', '.tif', '.tiff'}
SYSTEM_TESSDATA = '/opt/homebrew/share/tessdata'

# (name, tessdata_dir, oem)
# oem 1 = LSTM   (Tesseract 4/5 model)
# oem 0 = legacy (Tesseract 3.x model — indic-ocr sat)
MODELS = [
    ('sat',          SYSTEM_TESSDATA, '1'),   # our trained LSTM — use PSM 13 (raw line, no DAWG)
    ('sat_indicocr', SYSTEM_TESSDATA, '0'),   # legacy OEM 0 baseline
]

def levenshtein(a, b):
    if not a: return len(b)
    if not b: return len(a)
    prev = list(range(len(b)+1))
    for ca in a:
        curr = [prev[0]+1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(0 if ca==cb else 1)))
        prev = curr
    return prev[-1]

def cer(ref, hyp):
    ref, hyp = ref.strip(), hyp.strip()
    if not ref: return 0.0
    return levenshtein(ref, hyp) / len(ref)

def wer(ref, hyp):
    ref_w, hyp_w = ref.strip().split(), hyp.strip().split()
    if not ref_w: return 0.0
    return levenshtein(ref_w, hyp_w) / len(ref_w)

def space_recall(ref, hyp):
    ref_spaces = ref.count(' ')
    if ref_spaces == 0: return None
    return min(hyp.count(' ') / ref_spaces, 1.0)

def ocr(image_path, model, tessdata_dir, psm='7', oem='1'):
    result = subprocess.run(
        ['tesseract', str(image_path), 'stdout',
         '--tessdata-dir', tessdata_dir, '-l', model,
         '--psm', str(psm), '--oem', str(oem)],
        capture_output=True, text=True, errors='replace')
    out = result.stdout.strip()
    out = re.sub(r'Estimating resolution.*', '', out, flags=re.DOTALL).strip()
    out = re.sub(r'\n+', ' ', out).strip()
    return out

def find_gt(img_path):
    d = img_path.parent
    exact = d / (img_path.stem + '.gt.txt')
    if exact.exists(): return exact
    stem = re.sub(r'-\d+$', '', img_path.stem)
    fallback = d / (stem + '.gt.txt')
    return fallback if fallback.exists() else None

def collect_pairs(test_dir, force_psm=None):
    pairs, seen = [], set()
    for ext in IMAGE_EXTS:
        for img in sorted(Path(test_dir).glob(f'*{ext}')):
            gt = find_gt(img)
            if gt is None or str(gt) in seen: continue
            seen.add(str(gt))
            psm = str(force_psm) if force_psm else '7'
            pairs.append((img, gt, psm))
    return pairs

def run_benchmark(pairs, models=MODELS, verbose=False):
    results = {name: [] for name, _, _ in models}
    print(f"\n{'Image':<35} {'Model':<14} {'CER':>6} {'WER':>6} {'SpaceR':>8}  {'GT excerpt'}")
    print('─'*97)
    for img, gt_path, psm in pairs:
        gt_text = re.sub(r'\s+', ' ', gt_path.read_text(encoding='utf-8').strip())
        for name, td, oem in models:
            hyp = ocr(img, name, td, psm, oem)
            c = cer(gt_text, hyp)
            w = wer(gt_text, hyp)
            sr = space_recall(gt_text, hyp)
            results[name].append({'cer': c, 'wer': w, 'space_recall': sr,
                                  'gt': gt_text, 'hyp': hyp, 'img': img.name})
            sr_str = f"{sr:.2f}" if sr is not None else "  n/a"
            print(f"  {img.name:<33} {name:<14} {c:6.3f} {w:6.3f} {sr_str:>8}  {gt_text[:35]!r}")
            if verbose:
                print(f"    GT:  {gt_text[:80]!r}")
                print(f"    OCR: {hyp[:80]!r}")
    return results

def summary_table(results):
    n = len(next(iter(results.values())))
    print(f"\n{'='*78}")
    print(f"  SUMMARY — averages across {n} images")
    print(f"{'='*78}")
    print(f"  {'Model':<16} {'Engine':>6} {'Char Acc':>9} {'Word Acc':>9} {'avg CER':>8} {'avg WER':>8} {'SpaceR':>7}")
    print(f"  {'─'*74}")
    model_oem = {name: oem for name, _, oem in MODELS}
    engine_map = {'0': 'legacy', '1': 'LSTM'}
    for name, rows in results.items():
        avg_cer = sum(r['cer'] for r in rows) / len(rows)
        avg_wer = sum(r['wer'] for r in rows) / len(rows)
        sr_rows = [r['space_recall'] for r in rows if r['space_recall'] is not None]
        avg_sr = sum(sr_rows)/len(sr_rows) if sr_rows else 0.0
        engine = engine_map.get(model_oem.get(name, '1'), '?')
        print(f"  {name:<16}  {engine:>6}  {(1-avg_cer)*100:>7.1f}%  {(1-avg_wer)*100:>7.1f}%"
              f"  {avg_cer:>8.3f}  {avg_wer:>8.3f}  {avg_sr:>6.3f}")
    print(f"{'='*78}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-dir', default='test-images')
    parser.add_argument('--psm', default=None)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    pairs = collect_pairs(args.test_dir, force_psm=args.psm)
    print(f"Test images: {len(pairs)} ({args.test_dir})")
    results = run_benchmark(pairs, verbose=args.verbose)
    summary_table(results)

if __name__ == '__main__':
    main()
