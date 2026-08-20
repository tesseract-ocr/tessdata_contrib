#!/usr/bin/env python3
"""Recover the printed text of a Wikisource Page: scan from its wikitext.

These pages are the only real pre-reform ground truth in this build. Everything
else is rendered type, and rendered type keeps fita's crossbar in a way that a
library scan does not. So what this produces is the measuring stick, and a
measuring stick that is quietly wrong is worse than none.

Two traps are worth naming, because both produce output that looks perfectly
plausible.

The first is {{свр}}. A ru.wikisource Page: for a pre-reform book commonly holds
the text twice -- once as printed, then again transposed into modern spelling
after that marker. The modern half rewrites ѳ to ф and ѵ to и, which is to say
it rewrites away the entire subject of this project. Concatenating the halves
yields a file where about a quarter of the fita instances have become ф and
which scores a correct reading as an error. Everything from {{свр}} onward is
discarded here, and the check that this is the right half is not a reading of
the template's documentation but of the scan: the printed page ends
"КОНЕЦЪ ЧЕТВЕРТОЙ И ПОСЛѢДНЕЙ ЧАСТИ", with ъ and ѣ, and that line falls before
the marker.

The second is {{примечание ВТ}}, an editorial footnote by Wikisource's own
editors. Its text is not on the page at all -- it typically says "the original
begins with izhitsa" -- so folding it into the ground truth invents words the
printer never set, in exactly the letters being measured.

Unknown templates are an error rather than a silent drop. A template this does
not recognise is text of unknown status, and guessing at it is how the first
trap gets sprung a second time.
"""
import sys, re, html, argparse, unicodedata, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_training_text import unicharset_chars, NEW

ACUTE = '\u0301'                     # COMBINING ACUTE ACCENT
PIPE = '\x00PIPE\x00'                # stands in for {{!}} during arg splitting
MODERN = '{{свр}}'                   # start of the modern-orthography copy

# Templates whose sole argument is printed text.
PASS_FIRST = {'выступ', 'gb', 'razs', 'razr', 'нобр'}
# Templates whose printed form is a later argument.
PASS_LAST = {'lang'}                 # {{lang|la|Myoxus avellanarius}}
# Templates that render as a combining acute over the preceding letter.
ACCENT = {'акут', 'акут3', 'удар'}
# Formatting and editorial furniture that is not on the printed page. The
# footnote templates take their content with them.
DROP = {'indent', 'примечание вт', 'примечания вт',
        'свр', 'обавторе', 'razr2'}

# A page number supplied by the transcriber rather than read off the page is
# written in angle brackets. Everything inside {{колонтитул}} that is not so
# marked is ink.
SUPPLIED = re.compile(r'^<[^>]*>$')

# Transcription conventions rewritten to the mark the printer actually set.
# Wikisource spells the dash before a bare suffix ("−сный") with the
# mathematical minus, which is in no Cyrillic OCR unicharset and so is a mark
# the model cannot emit at any quality. Left alone it is a scored error that no
# amount of training could remove.
NORMALIZE = {'\u2212': '-'}          # MINUS SIGN -> HYPHEN-MINUS


def tsdl(args):
    """A cross-reference to another dictionary entry.

    {{tsdl|ящаръ}} prints "ящаръ"; {{tsdl|Ящик|ящикъ}} prints the second
    argument; a trailing "so" is a display flag and not text. This one appears
    both inside editorial footnotes, where it is discarded with them, and in
    running text, where it is printed.
    """
    args = [a for a in args if a.strip() != 'so']
    return args[1] if len(args) > 1 else (args[0] if args else '')


def render(body):
    """One template, already free of nested templates, as printed text."""
    args = body.split('|')
    name = args[0].strip()
    # MediaWiki treats the first letter of a template name as case-insensitive,
    # so {{Выступ}} and {{выступ}} are one template.
    key = (name[:1].lower() + name[1:]).lower()
    rest = args[1:]
    if key in ACCENT:
        return ACUTE
    if key in DROP:
        return ''
    if key == 'колонтитул':
        # The running head, left/centre/right. Printed on the 1882 page and
        # absent from the 1866 one, so it cannot simply be discarded: dropping
        # a head that is really there leaves the OCR reading characters the
        # transcription does not contain, and the 1882 head happens to end in
        # "ѵпостасный", which would be scored as a spurious izhitsa in the one
        # metric this project exists to protect.
        return ' '.join(a.strip() for a in rest
                        if a.strip() and not SUPPLIED.match(a.strip()))
    if key == 'tsdl':
        return tsdl(rest)
    if key in PASS_FIRST:
        # Everything after the first '|', not just the first argument: a
        # hanging-indent block legitimately contains '|' of its own.
        return body.split('|', 1)[1] if len(args) > 1 else ''
    if key in PASS_LAST:
        return rest[-1] if rest else ''
    raise KeyError(name)


INNERMOST = re.compile(r'\{\{([^{}]*)\}\}')


def expand(text):
    """Expand templates from the inside out. Returns (text, unknown names)."""
    unknown = set()
    while True:
        m = INNERMOST.search(text)
        if not m:
            return text, unknown
        try:
            out = render(m.group(1))
        except KeyError as e:
            unknown.add(e.args[0])
            out = ''
        text = text[:m.start()] + out + text[m.end():]


def convert(wikitext, keep_accents=False):
    """Wikitext of a Page: as printed text. Returns (text, report)."""
    rep = {}
    cut = wikitext.find(MODERN)
    rep['modern_copy_dropped'] = cut >= 0
    if cut >= 0:
        wikitext = wikitext[:cut]

    # ProofreadPage keeps the running head, the pagequality stamp and the
    # footnote block in <noinclude>, because none of it should follow the page
    # into a transcluded chapter. But the head is ink -- it is printed at the
    # top of the scan and the OCR will read it -- so it is lifted out before
    # the block is discarded, and put back as the first line, which is where
    # the printer set it.
    head = ''
    m = re.search(r'\{\{[Кк]олонтитул\|[^{}]*\}\}', wikitext)
    if m:
        head = render(m.group(0)[2:-2])
    rep['running_head'] = head

    # The blocks at the top and bottom of a Page: are routinely left unclosed.
    t = re.sub(r'<noinclude>.*?</noinclude>', '', wikitext, flags=re.S)
    t = re.sub(r'^.*?</noinclude>', '', t, flags=re.S)
    t = re.sub(r'<noinclude>.*$', '', t, flags=re.S)
    if head:
        t = head + '\n' + t

    t = t.replace('{{!}}', PIPE)
    t, unknown = expand(t)
    rep['unknown_templates'] = sorted(unknown)
    t = t.replace(PIPE, '|')

    # An inline glyph image stands where the printer set a character that has no
    # Unicode equivalent -- here the Cyrillic numeral nine. It is a real mark on
    # the page that the ground truth cannot spell, so it is removed and counted.
    t, n = re.subn(r'\[\[\s*(?:Файл|File|Image|Изображение):[^\]]*\]\]', '', t)
    rep['glyph_images_dropped'] = n
    t = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', t)
    t = re.sub(r'\[\[([^\]]*)\]\]', r'\1', t)

    t = re.sub(r'<\s*section\b[^>]*>', '', t)
    t = re.sub(r'<[^>]+>', '', t)          # small, big, center, div, br, refs
    t = t.replace('__NOEDITSECTION__', '')
    t = re.sub(r"'{2,}", '', t)            # bold and italic markup
    t = html.unescape(t)
    for src, dst in NORMALIZE.items():
        t = t.replace(src, dst)

    if not keep_accents:
        t = unicodedata.normalize('NFD', t)
        t, n = re.subn(ACUTE, '', t)
        t = unicodedata.normalize('NFC', t)
        rep['accents_stripped'] = n

    lines = [' '.join(l.split()) for l in t.split('\n')]
    t = '\n'.join(l for l in lines if l)
    return t, rep


def main():
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('wikitext')
    ap.add_argument('out')
    ap.add_argument('--unicharset',
                    help='report characters this model could never emit')
    ap.add_argument('--keep-accents', action='store_true',
                    help='keep combining acute; the 137-entry unicharset has '
                         'no code for it, so the default is to strip')
    a = ap.parse_args()

    src = pathlib.Path(a.wikitext).read_text(encoding='utf-8')
    text, rep = convert(src, a.keep_accents)

    if rep['unknown_templates']:
        sys.exit('ERROR: unhandled templates, text status unknown: '
                 + ', '.join(rep['unknown_templates']))

    pathlib.Path(a.out).write_text(text + '\n', encoding='utf-8')

    print(f'wrote {a.out}')
    print(f"    {len(text.splitlines())} lines, {len(text)} chars")
    print(f"    modern-orthography copy dropped: {rep['modern_copy_dropped']}")
    print(f"    glyph images dropped: {rep['glyph_images_dropped']}")
    if 'accents_stripped' in rep:
        print(f"    combining acutes stripped: {rep['accents_stripped']}")
    for ch in NEW:
        print(f'    {ch} U+{ord(ch):04X}  {text.count(ch)}')
    if a.unicharset:
        ok = unicharset_chars(a.unicharset) | {'\n'}
        bad = sorted(set(text) - ok)
        if bad:
            print(f'    NOT EMITTABLE by this model ({len(bad)} distinct):')
            for c in bad:
                print(f'        U+{ord(c):04X} {unicodedata.name(c, "?"):<34}'
                      f' x{text.count(c)}')
        else:
            print('    every character is emittable by this model')


if __name__ == '__main__':
    main()
