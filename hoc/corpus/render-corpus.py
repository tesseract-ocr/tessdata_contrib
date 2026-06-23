#!/usr/bin/env python3
"""
render-corpus.py

Renders corpus/sat_corpus.txt with 4 font variants into rendered/ as PNG + gt.txt pairs.
Each line × 4 fonts = one training image each.

Fonts used:
  NotoSansWarangCiti Regular  — letterpress-style upright
  NotoSansWarangCiti Italic   — letterpress-style slanted
  NotoSansWarangCiti Regular — clean sans-serif
  NotoSansWarangCiti Bold    — bold weight variation

Output: rendered/<font_tag>_line<N>.{png,gt.txt}
"""

from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

BASE   = Path(__file__).parent
CORPUS = BASE / "corpus" / "sat_corpus.txt"
OUTDIR = BASE / "rendered"
OUTDIR.mkdir(exist_ok=True)

FONTS = [
    ("gurugomke_reg",    BASE / "NotoSansWarangCiti-Regular.ttf",         36),
    ("gurugomke_ital",   BASE / "NotoSansWarangCiti-Italic.ttf",          36),
    ("noto_olchiki_reg", BASE / "NotoSansWarangCiti-Regular.ttf",   36),
    ("noto_olchiki_bld", BASE / "NotoSansWarangCiti-Bold.ttf",      36),
]

PAD_X = 20
PAD_Y = 12
MIN_H = 60   # upscale short crops so Tesseract doesn't refuse them

lines = [l.rstrip('\n') for l in CORPUS.read_text(encoding='utf-8').splitlines() if l.strip()]

total = 0
for tag, font_path, size in FONTS:
    font = ImageFont.truetype(str(font_path), size)
    for idx, text in enumerate(lines):
        # measure text size
        dummy = Image.new("L", (1, 1))
        bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0] + PAD_X * 2
        h = max(bbox[3] - bbox[1] + PAD_Y * 2, MIN_H)

        img = Image.new("L", (w, h), 255)
        draw = ImageDraw.Draw(img)
        draw.text((PAD_X, PAD_Y), text, font=font, fill=0)

        stem = OUTDIR / f"{tag}_line{idx:04d}"
        img.save(str(stem) + ".png")
        (stem.parent / (stem.name + ".gt.txt")).write_text(text, encoding="utf-8")
        total += 1

    print(f"  {tag}: {len(lines)} images")

print(f"\nTotal rendered: {total} PNG+gt.txt pairs → {OUTDIR}")
