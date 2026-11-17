"""Page rendering and the background normalisation that makes scans readable.

`normalize` is the single highest-yield thing in this package. Tesseract
binarises with a global Otsu threshold, which assumes the page has two grey
levels. A library scan has three: black ink on grey paper, inside the pure
white surround of the scanner bed. When the page is sparsely inked the largest
between-class variance is not ink against paper but paper against surround, so
the threshold lands between them, four fifths of the sheet is classified as
ink, and layout analysis returns nothing.

The failure is silent. Tesseract exits 0, prints nothing on stderr, and takes
about a fifth of a second. The page is simply gone, and it looks exactly like a
blank leaf. In one corpus of 25 scanned books this had swallowed 700 pages, of
which 650 came back after normalisation -- 1.73 million characters that the
first pass reported as empty without any error at all.

So do not treat an empty page as a blank page. Retry it normalised, and if it
is still empty, measure the ink (see quality.ink).
"""
import os, subprocess

import numpy as np
from PIL import Image, ImageFilter

DPI = 300


def run(cmd):
    """subprocess.run that will not raise on undecodable output.

    Leptonica echoes raw file bytes into its own error messages, so tesseract's
    stderr is not always valid UTF-8. `text=True` would raise UnicodeDecodeError
    from inside the call, and a caller that wraps OCR in try/except would record
    that as an empty page -- turning a diagnostic into data loss.
    """
    p = subprocess.run(cmd, capture_output=True)
    return subprocess.CompletedProcess(
        p.args, p.returncode,
        p.stdout.decode('utf-8', 'replace'),
        p.stderr.decode('utf-8', 'replace'))


def normalize(path, block=8, median=5, level=200):
    """Flatten an uneven or dark scan background. Returns the new file's path.

    The background is estimated by shrinking the page by `block`, median
    filtering to remove the text, and stretching it back; subtracting that from
    the original leaves the ink and levels the paper at `level`.

    Two properties are relied on elsewhere and should be preserved by any
    replacement. The output has the same width and height as the input, so hOCR
    character boxes measured on one are valid on the other; and it maps ink to
    about 72 against paper at about 200, so a dark test at 128 still separates
    them (glyph.bar_position depends on exactly that).
    """
    g = Image.open(path).convert('L')
    w, h = g.size
    bg = (g.resize((max(1, w // block), max(1, h // block)), Image.BILINEAR)
           .filter(ImageFilter.MedianFilter(median))
           .resize((w, h), Image.BILINEAR))
    n = (np.asarray(g).astype(np.int16)
         - np.asarray(bg).astype(np.int16) + level)
    out = os.path.splitext(path)[0] + '_n.png'
    Image.fromarray(np.clip(n, 0, 255).astype(np.uint8)).save(out)
    return out


def render(pdf, page, outdir, dpi=DPI):
    """One page of a PDF as a greyscale PNG, or None if it will not render."""
    pref = os.path.join(outdir, f'p{page:05d}')
    run(['pdftoppm', '-r', str(dpi), '-gray', '-f', str(page), '-l', str(page),
         '-png', pdf, pref])
    for f in sorted(os.listdir(outdir)):
        if f.startswith(f'p{page:05d}') and f.endswith('.png'):
            return os.path.join(outdir, f)
    return None


def load(png):
    return np.asarray(Image.open(png).convert('L'))


def hocr(png, lang, psm=3):
    """hOCR with character boxes, which is what the te measurement needs.

    `hocr_char_boxes=1` is what makes tesseract emit ocrx_cinfo spans carrying
    x_bboxes; without it the hOCR has word boxes only and an individual glyph
    cannot be located on the page.
    """
    return run(['tesseract', png, 'stdout', '-l', lang, '--psm', str(psm),
                '-c', 'hocr_char_boxes=1', 'hocr']).stdout


def text(png, lang, psm=3):
    return run(['tesseract', png, 'stdout', '-l', lang, '--psm', str(psm)]).stdout


def ocr_image(png, lang, min_chars=200, reader=None):
    """OCR, retrying on a normalised copy when the first pass comes back thin.

    This is the wrapper that every call should go through. Calling tesseract
    directly is how the 700 pages were lost.
    """
    reader = reader or (lambda p: text(p, lang))
    out = reader(png)
    if len(out.strip()) >= min_chars:
        return out, 'raw'
    try:
        npng = normalize(png)
    except Exception:
        return out, 'raw'
    out2 = reader(npng)
    if len(out2.strip()) > len(out.strip()):
        return out2, 'normalized'
    return out, 'raw'


def columns(page, lo=0.33, hi=0.62, min_ink=25):
    """Gutter x for a two-column page, None for one column or a blank page.

    Column-per-language books -- a Slavic name against its German gloss -- must
    be split before OCR, because tesseract will otherwise read across the
    gutter and interleave the two languages line by line.
    """
    H, W = page.shape
    ink = (page[int(H * 0.12):int(H * 0.88)] < 100).sum(axis=0).astype(float)
    ink = np.convolve(ink, np.ones(15) / 15, mode='same')
    if ink.max() < min_ink:
        return None
    body = ink[int(W * 0.08):int(W * 0.92)]
    med = np.median(body[body > ink.max() * 0.05]) if (body > 0).any() else 0
    a, b = int(W * lo), int(W * hi)
    j = a + int(np.argmin(ink[a:b]))
    if med <= 0 or ink[j] / med > 0.15:
        return None
    return j
