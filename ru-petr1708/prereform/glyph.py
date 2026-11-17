"""The three-legged te of pre-1850 civil type, which every OCR model reads as sha.

In the civil type of the eighteenth and early nineteenth century, lowercase te
is set as a three-legged letter: it is sha rotated 180 degrees. The two are
perfectly distinguishable to a reader, because the continuous horizontal bar
sits at the top of a te and at the bottom of a sha -- compare свѣтъ тень,
which in that type reads as if it were свᲇᲅᲆ ᲅᲇнь. No installed model was
trained on the form, so tesseract emits sha for both, and a book set in it comes
out with several thousand real words silently misspelled.

The evidence is not lost, though. It is still in the image, and the image can be
addressed through the character box that tesseract itself reports, so the letter
can be measured rather than guessed at.

What defeats the naive test is serifs. The three legs of a sha end in serifs
that put ink along the top edge as well, so counting ink above against ink below
says nothing at all. The bar is told from the serifs by continuity, not by
quantity: the bar spans the glyph, three serifs do not. Hence the feature is the
longest unbroken run of dark pixels in a row.

Calibrated on Moroshkin 1867, a book whose type already distinguishes the two:
there sha measures -0.17 and te +0.30 on this scale, and the sign comes out
right for every reference letter with a known bar (pe, top; tse, bottom). On
Trudy 1820s, 28 of 35 glyphs read as sha measure as top-barred, so they are
really te.

The test is self-limiting, which is what makes it safe to apply everywhere. On
a document set in modern type the sha are genuinely bottom-barred, nothing is
relabelled, and the pass costs only the time to measure. Measured shares over
six pre-reform books ran 75 per cent in Trudy and 33 in Pacic against 1 to 5
per cent in the other four; a book either sets the three-legged te or it does
not, and the measurement says which without being told.
"""
import re

import numpy as np

CINFO = re.compile(
    r"<span class='ocrx_cinfo' title='x_bboxes (-?\d+) (-?\d+) (-?\d+) (-?\d+);"
    r"[^']*'>(.*?)</span>")
LINE_BBOX = re.compile(
    r"<span class='ocr_line'[^>]*title=\"bbox (\d+) (\d+) (\d+) (\d+)")
STRUCT = re.compile(
    r"<span class='ocrx_cinfo'[^>]*>.*?</span>"
    r"|<span class='ocrx_word'"
    r"|<span class='ocr_line'[^>]*title=\"bbox \d+ \d+ \d+ \d+")
ENT = [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
       ('&quot;', '"'), ('&#39;', "'")]

# Above this the glyph is called a te. Zero would be the natural cut, but the
# calibration puts sha at -0.17 and te at +0.30, so a small positive threshold
# sits in the gap and costs only the most doubtful glyphs.
THRESH = 0.05

# Below these the box is too small for a run-length to mean anything.
MIN_H, MIN_W = 12, 8

# A bar must span most of the glyph. Three serifs do not reach this.
MIN_RUN = 0.55


def unescape(s):
    for k, v in ENT:
        s = s.replace(k, v)
    return s


def bar_position(g):
    """+1 for a continuous bar at the top, -1 at the bottom, None for neither.

    `g` is the glyph's greyscale box as a numpy array. The return is
    (top - bottom) / (top + bottom) over the longest dark run in any row of the
    top and bottom thirds, so it is scale-free and does not depend on how much
    ink the letter has.
    """
    if g.size == 0 or g.shape[0] < MIN_H or g.shape[1] < MIN_W:
        return None
    d = g < 128
    h, w = d.shape
    # Longest run of dark pixels per row, vectorised over the glyph.
    runs = np.zeros(h)
    cur = np.zeros(h, dtype=int)
    for x in range(w):
        cur = np.where(d[:, x], cur + 1, 0)
        runs = np.maximum(runs, cur)
    runs = runs / w
    k = max(2, h // 3)
    top, bot = runs[:k].max(), runs[-k:].max()
    if max(top, bot) < MIN_RUN:
        return None
    return (top - bot) / (top + bot)


def lines(hocr_xml, page, fix_te=True, thresh=THRESH):
    """[(y_top, y_bottom, text)], te_relabelled, sha_kept -- for one page.

    `page` is the greyscale page as a numpy array in the same coordinate frame
    as the hOCR, so a cropped column must be passed already cropped.

    The two counts are the diagnostic. Their ratio is the share of sha that
    measured as te, which is what tells you whether the book uses the form at
    all, and it is the right thing to gate the stem repairs on (see
    repair.lexical_pass).
    """
    out, fixed, kept = [], 0, 0
    buf, y0, y1 = [], 0, 0
    for m in STRUCT.finditer(hocr_xml):
        tok = m.group(0)
        if tok.startswith("<span class='ocr_line'"):
            if buf:
                out.append((y0, y1, ''.join(buf).strip()))
            _, y0, _, y1 = (int(v) for v in LINE_BBOX.match(tok).groups())
            buf = []
        elif tok.startswith("<span class='ocrx_word'"):
            buf.append(' ')
        else:
            c = CINFO.match(tok)
            if not c:
                continue
            x1, ya, x2, yb = (int(v) for v in c.groups()[:4])
            ch = unescape(c.group(5))
            if fix_te and ch in ('ш', 'Ш'):
                v = bar_position(page[max(0, ya):yb, max(0, x1):x2])
                if v is not None and v > thresh:
                    ch = 'т' if ch == 'ш' else 'Т'
                    fixed += 1
                else:
                    kept += 1
            buf.append(ch)
    if buf:
        out.append((y0, y1, ''.join(buf).strip()))
    return [l for l in out if l[2]], fixed, kept


def te_share(fixed, kept):
    """Share of glyphs read as sha that measured as te. 0.0 when none were."""
    return fixed / (fixed + kept) if fixed + kept else 0.0
