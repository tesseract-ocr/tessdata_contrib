#!/usr/bin/env python3
"""Generate noise-augmented copies of synthetic line images for OCR training.

Takes clean synthetic rendered lines and applies realistic degradation
(blur, noise, contrast shifts, slight rotation) to simulate scan-like
conditions. This bridges the distribution gap between clean renders
and real scanned documents.

Output: augmented PNG + copied .box → tesseract lstm.train → .lstmf
"""
import sys, shutil, subprocess, random
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

RENDERED_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("lstmf/rendered")
OUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("lstmf/augmented")
TESSDATA = "tessdata_best"
PER_SOURCE = int(sys.argv[3]) if len(sys.argv) > 3 else 25

random.seed(42)
np.random.seed(42)

OUT_DIR.mkdir(parents=True, exist_ok=True)

sources = {}
for f in sorted(RENDERED_DIR.glob("*.lstmf")):
    prefix = f.stem.rsplit("_line", 1)[0]
    sources.setdefault(prefix, []).append(f.stem)

def degrade(img):
    arr = np.array(img.convert("L"))

    # Gaussian-like blur (slight)
    img_out = Image.fromarray(arr)
    radius = random.uniform(0.3, 1.2)
    img_out = img_out.filter(ImageFilter.GaussianBlur(radius=radius))

    # Salt-and-pepper noise
    arr2 = np.array(img_out)
    noise_density = random.uniform(0.005, 0.02)
    salt = np.random.random(arr2.shape) < noise_density / 2
    pepper = np.random.random(arr2.shape) < noise_density / 2
    arr2[salt] = 255
    arr2[pepper] = 0
    img_out = Image.fromarray(arr2)

    # Contrast variation
    factor = random.uniform(0.7, 1.3)
    img_out = ImageEnhance.Contrast(img_out).enhance(factor)

    # Brightness variation (simulates uneven scan exposure)
    bright = random.uniform(0.85, 1.15)
    img_out = ImageEnhance.Brightness(img_out).enhance(bright)

    # Slight rotation (simulates scan skew)
    angle = random.uniform(-0.8, 0.8)
    img_out = img_out.rotate(angle, fillcolor=255, expand=False)

    return img_out.convert("L")

total_ok = 0
total_fail = 0

for prefix, stems in sorted(sources.items()):
    selected = random.sample(stems, min(PER_SOURCE, len(stems)))
    ok = fail = 0

    for stem in selected:
        src_png = RENDERED_DIR / f"{stem}.png"
        src_box = RENDERED_DIR / f"{stem}.box"
        if not src_png.exists() or not src_box.exists():
            fail += 1
            continue

        aug_stem = f"aug_{stem}"
        dst_png = OUT_DIR / f"{aug_stem}.png"
        dst_box = OUT_DIR / f"{aug_stem}.box"
        dst_lstmf = OUT_DIR / f"{aug_stem}.lstmf"

        if dst_lstmf.exists():
            ok += 1
            continue

        img = Image.open(src_png)
        degraded = degrade(img)
        degraded.save(dst_png)
        shutil.copy2(src_box, dst_box)

        made = False
        for psm in ("7", "6", "10"):
            subprocess.run(
                ["tesseract", str(dst_png), str(OUT_DIR / aug_stem),
                 "--tessdata-dir", TESSDATA,
                 "--dpi", "300", "--psm", psm,
                 "-l", "sat_base", "lstm.train"],
                capture_output=True, text=True
            )
            if dst_lstmf.exists():
                made = True
                break

        if made:
            ok += 1
        else:
            dst_png.unlink(missing_ok=True)
            dst_box.unlink(missing_ok=True)
            fail += 1

    print(f"  {prefix}: {ok} OK, {fail} failed (of {len(selected)} selected)")
    total_ok += ok
    total_fail += fail

print(f"\nTotal: {total_ok} augmented lstmf files created, {total_fail} failed")
