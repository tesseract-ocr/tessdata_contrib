#!/usr/bin/env python3
"""OCR one page of a pre-reform scan, with every stage of the pipeline shown.

This is the whole package on one page, in the order the stages have to run:
render, normalise, hOCR with character boxes, measure the three-legged te,
rejoin broken words, repair against the lexicon.

    python3 examples/ocr_page.py BOOK.pdf 41 [orusd]

The te measurement and the stem repairs are reported separately from the
result, because they are the two things that need watching on a book you have
not run before. A te share near zero means the book does not set the letter and
the stem repairs will be skipped, which is correct rather than a failure.
"""
import sys, os, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prereform import image, glyph, lexicon, repair, quality

# Below this share of sha measuring as te, the book is taken not to set the
# three-legged form and the stem repairs stay off. See repair.lexical_pass.
SHAPE_SHARE = 0.15


def main(pdf, page, lang='orusd'):
    page = int(page)
    work = tempfile.mkdtemp()

    png = image.render(pdf, page, work)
    if not png:
        sys.exit(f'page {page} did not render')

    # Normalise unconditionally here. In a batch run the retry in
    # image.ocr_image is cheaper, but the te measurement reads pixels from
    # whichever image the hOCR boxes were measured on, so the two must agree.
    npng = image.normalize(png)
    arr = image.load(npng)
    print(f'page {page}: {arr.shape[1]}x{arr.shape[0]}  '
          f'ink {quality.ink(npng)}')

    xml = image.hocr(npng, lang)
    ls, fixed, kept = glyph.lines(xml, arr)
    share = glyph.te_share(fixed, kept)
    print(f'sha glyphs: {fixed} measured as te, {kept} kept  -> share {share:.2f}'
          f'  ({"stem repairs on" if share > SHAPE_SHARE else "stem repairs off"})')

    txt = '\n'.join(l[2] for l in ls)
    txt, joined = repair.dehyphenate(txt)

    vocab = lexicon.words()
    before, ntok = lexicon.hit_rate(txt, vocab)
    txt, changed = repair.lexical_pass(txt, vocab, shape=share > SHAPE_SHARE)
    after, _ = lexicon.hit_rate(txt, vocab)

    print(f'hyphens rejoined: {joined}   tokens repaired: {changed}')
    print(f'lexicon hit rate: {before:.3f} -> {after:.3f} over {ntok} tokens')
    print(f'long_share: {quality.long_share(txt):.3f}')
    print('-' * 70)
    print(txt)


if __name__ == '__main__':
    if not 3 <= len(sys.argv) <= 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
