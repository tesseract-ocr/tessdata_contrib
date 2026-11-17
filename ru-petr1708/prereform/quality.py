"""Is this page text, is it noise, or is the leaf blank?

Three different questions, and they need three different instruments.

`long_share` separates text from noise, and is the acceptance test for a page
recovered by re-OCR. Real text spends its letters inside long words; noise
scatters them across fragments.

`ink` separates a blank leaf from a page the OCR failed on. This one cannot be
answered from the text at all -- OCR returns nothing in both cases -- so it is
answered from the image.

Both take a threshold, and the thresholds do not transfer between genres. See
the warning on long_share.
"""
import re

import numpy as np
from PIL import Image

ALPHA = re.compile(r'[A-Za-zÀ-ſ\u0400-\u04FF]{4,}')
ANY_ALPHA = re.compile(r'[A-Za-zÀ-ſ\u0400-\u04FF]')

# Calibrated on Latin prose. Do not transplant it without re-measuring; see
# below.
LONG_SHARE = 0.64

# A page with fewer letters than this is not worth keeping, but note the floor
# is on letters and not on characters. An earlier version cut at 200 characters
# and silently discarded real section headings.
MIN_ALPHA = 20


def n_alpha(txt):
    return sum(len(t) for t in ALPHA.findall(txt))


def long_share(txt):
    """Share of a page's letters that sit in tokens of four or more.

    WARNING. The 0.64 figure above was calibrated on running Latin prose and
    does not transfer to every genre. Measured against pages known to be good:
    lists of short Slavic name-elements score 0.494 to 0.591, and dense
    citation apparatus 0.642 -- all genuine, all at or below the cut. Before
    using this as a gate on a new corpus, measure it on pages of that corpus
    which are known to have read correctly, and where the count of doubtful
    pages is small enough, read them instead of thresholding them.
    """
    total = len(ANY_ALPHA.findall(txt))
    return n_alpha(txt) / total if total else 0.0


def ink(png, margin=0.04, dark=128, row_thresh=0.01):
    """Measure the ink on a page image. Pass a *normalised* image.

    Returns share of dark pixels as a percentage, the number of rows carrying
    any appreciable ink, and the densest single row.

    For scale: over two dozen scanned books, pages of type measured 5 to 13 per
    cent ink over 1400 to 2300 rows, while blank leaves measured 0.0 to 0.084
    per cent over at most 43 rows. That is three orders of magnitude, so the
    verdict is rarely in doubt.

    Ink without type is the case to watch, and it is not rare: in one corpus the
    two pages that had ink but no text turned out to be an engraved library
    bookplate with handwritten shelfmarks, and a marbled endpaper whose 620
    inked rows were paper texture. Look at anything that measures high and
    reads empty; do not assume the OCR failed.

    The outermost `margin` is ignored as scanner edge and page curl.
    """
    a = np.asarray(Image.open(png).convert('L')) if isinstance(png, str) else png
    H, W = a.shape
    d = a < dark
    inner = d[int(H * margin):int(H * (1 - margin)),
              int(W * margin):int(W * (1 - margin))]
    rows = inner.mean(axis=1)
    return {'ink': round(float(inner.mean()) * 100, 3),
            'textrows': int((rows > row_thresh).sum()),
            'band': round(float(rows.max()) * 100, 1)}


def undecodable(txt):
    """Share of characters that are control codes other than whitespace.

    A PDF whose embedded font has no usable ToUnicode map extracts as a run of
    U+0001, one per glyph. The text is the right length and the right shape, so
    a length check passes and a word-quality check that looks only at letters
    can score it high while the page in fact contains no letters at all. One
    857-page book in this corpus was 55.9 per cent U+0001 with zero letters in
    the body, and had been accepted at a measured quality of 0.996.

    Anything above a fraction of a per cent means the text layer must be
    discarded and the document OCRed from the page images.
    """
    if not txt:
        return 0.0
    bad = sum(1 for c in txt if ord(c) < 32 and c not in '\n\r\t\f')
    return bad / len(txt)
