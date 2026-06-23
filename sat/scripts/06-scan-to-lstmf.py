#!/usr/bin/env python3
"""
06-scan-to-lstmf.py

Splits a scanned page + ground-truth text file into individual line
training pairs and converts them to .lstmf files using the same
cluster-box format as 02-make-lstmf.sh.

Usage:
  cd sat-tesseract-training/
  python3 06-scan-to-lstmf.py <image> <gt.txt> [--prefix ganam]
"""

import argparse
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image

# ── Paths (relative to sat-tesseract-training/) ───────────────────────────────
TESSDATA_BEST = "tessdata_best"
SCAN_LSTMF    = Path("lstmf/scan")
LIST_FILE     = Path("lstmf/list.txt")

# ── Line detection ─────────────────────────────────────────────────────────────
ROW_THR      = 0.05   # fraction of row-max to count as text row
MIN_HEIGHT   = 6      # min px height to keep a region
SPARSE_FRAC  = 0.22   # regions with peak below this × median → skip (stray mark)
UPSCALE      = 2      # upscale factor for better pixel density
VPAD         = 4      # vertical padding in original pixels around each line

def detect_lines(gray_arr):
    binary = gray_arr < 180
    proj   = binary.sum(axis=1)
    thr    = proj.max() * ROW_THR
    lines, in_text, start = [], False, 0
    for i, v in enumerate(proj):
        if v > thr and not in_text:
            start, in_text = i, True
        elif v <= thr and in_text:
            if i - start >= MIN_HEIGHT:
                lines.append((start, i, int(proj[start:i].max())))
            in_text = False
    if in_text and (len(proj) - start) >= MIN_HEIGHT:
        lines.append((start, len(proj), int(proj[start:].max())))
    return lines

def filter_lines(lines):
    if not lines:
        return [], []
    peaks   = sorted(pk for _, _, pk in lines)
    med_pk  = peaks[len(peaks) // 2]
    sparse  = med_pk * SPARSE_FRAC
    heights = sorted(e - s for s, e, _ in lines)
    med_h   = heights[len(heights) // 2]
    kept, skipped = [], []
    last = len(lines) - 1
    dense = med_pk * 1.5
    for i, (s, e, pk) in enumerate(lines):
        if i == 0 and ((e - s) > med_h * 1.3 or pk > dense):
            skipped.append(i)
            continue
        if i == last and (e - s) > med_h * 1.25:
            skipped.append(i)
            continue
        if (e - s) > med_h * 1.7:               # any line much taller than median → non-body element
            skipped.append(i)
            continue
        if pk < sparse:                          # very sparse → stray mark
            skipped.append(i)
            continue
        kept.append((s, e, pk))
    return kept, skipped

# ── Ol Chiki helpers ──────────────────────────────────────────────────────────
def is_ol_chiki(c):
    return 0x1C50 <= ord(c) <= 0x1C7F

def ol_chiki_clusters(text):
    clusters, chars, i = [], list(text), 0
    while i < len(chars):
        c = chars[i]; cl = c; i += 1
        while i < len(chars) and unicodedata.category(chars[i]) in ('Lm', 'Mn', 'Mc', 'Cf'):
            cl += chars[i]; i += 1
        clusters.append(cl)
    return [c for c in clusters if c.strip()]

# ── lstmf creation ────────────────────────────────────────────────────────────
def make_lstmf(png_path, gt_text):
    """Create cluster-format box file and run tesseract lstm.train."""
    png_path = Path(png_path)
    img  = Image.open(png_path)
    W, H = img.size

    clusters = ol_chiki_clusters(gt_text)
    if not clusters:
        return False

    # Write .gt.txt (needed by 02-make-lstmf if re-run later)
    png_path.with_suffix('.gt.txt').write_text(gt_text + '\n', encoding='utf-8')

    # Cluster-format box file: equal-width x-slices, one per cluster
    box_path = png_path.with_suffix('.box')
    n  = len(clusters)
    cw = W / n
    lines = [f"{c} {int(i*cw)} 0 {int((i+1)*cw)} {H} 0"
             for i, c in enumerate(clusters)]
    lines.append("\t 0 0 1 1 0")
    box_path.write_text("\n".join(lines) + "\n", encoding='utf-8')

    # PSM 7 → 6 → 10 fallback (same order as 02-make-lstmf.sh)
    lstmf = png_path.with_suffix('.lstmf')
    for psm in ("7", "6", "10"):
        subprocess.run(
            ["tesseract", str(png_path), str(png_path.with_suffix('')),
             "--tessdata-dir", TESSDATA_BEST,
             "--dpi", "300", "--psm", psm,
             "-l", "sat_base", "lstm.train"],
            capture_output=True, text=True
        )
        if lstmf.exists():
            return True
    return False

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    parser.add_argument('gt')
    parser.add_argument('--prefix', default=None)
    args = parser.parse_args()

    prefix = args.prefix or Path(args.image).stem

    img      = Image.open(args.image).convert('RGB')
    gray_arr = np.array(img.convert('L'))

    # Load GT: keep only non-blank lines with Ol Chiki chars
    raw_gt   = Path(args.gt).read_text(encoding='utf-8').splitlines()
    gt_lines = [ln.strip() for ln in raw_gt
                if ln.strip() and any(is_ol_chiki(c) for c in ln)]

    print(f"\n  Image:    {args.image}  ({img.size[0]}×{img.size[1]}px)")
    print(f"  GT lines: {len(gt_lines)}")

    all_lines          = detect_lines(gray_arr)
    kept, skipped_idx  = filter_lines(all_lines)

    print(f"  Detected: {len(all_lines)} regions  →  kept {len(kept)}, "
          f"skipped {len(skipped_idx)} (indices: {skipped_idx})")

    if len(kept) != len(gt_lines):
        print(f"\n  MISMATCH: {len(kept)} image lines vs {len(gt_lines)} GT lines")
        print("\n  All detected regions:")
        for i, (s, e, pk) in enumerate(all_lines):
            tag = 'SKIP' if i in skipped_idx else 'keep'
            print(f"    L{i+1:02d}  y={s}–{e}  h={e-s}px  peak={pk}  [{tag}]")
        print("\n  GT lines:")
        for i, ln in enumerate(gt_lines):
            print(f"    {i+1:2d}: {ln[:60]}")
        sys.exit(1)

    SCAN_LSTMF.mkdir(parents=True, exist_ok=True)

    # Track existing list entries to avoid duplicates
    existing = set()
    if LIST_FILE.exists():
        existing = set(LIST_FILE.read_text(encoding='utf-8').splitlines())

    ok = fail = 0
    new_paths = []

    print()
    for idx, ((y0, y1, _), gt_text) in enumerate(zip(kept, gt_lines)):
        name     = f"{prefix}_line{idx+1:04d}"
        png_path = SCAN_LSTMF / f"{name}.png"
        lstmf    = SCAN_LSTMF / f"{name}.lstmf"

        # Crop line with padding, upscale 2×
        H_orig, W_orig = gray_arr.shape
        top    = max(0, y0 - VPAD)
        bottom = min(H_orig, y1 + VPAD)
        line_img = img.crop((0, top, W_orig, bottom))
        line_img = line_img.resize(
            (line_img.width * UPSCALE, line_img.height * UPSCALE),
            Image.LANCZOS
        )
        line_img.save(str(png_path))

        if make_lstmf(png_path, gt_text):
            ok += 1
            abs_path = str(lstmf.resolve())
            if abs_path not in existing:
                new_paths.append(abs_path)
            preview = gt_text[:55] + ('…' if len(gt_text) > 55 else '')
            print(f"  OK  {name}  {preview}")
        else:
            fail += 1
            print(f"  FAIL {name}")

    if new_paths:
        with LIST_FILE.open('a', encoding='utf-8') as f:
            for p in new_paths:
                f.write(p + '\n')

    total = sum(1 for ln in LIST_FILE.read_text(encoding='utf-8').splitlines() if ln.strip())

    print(f"\n  Done: {ok} OK, {fail} failed")
    print(f"  Added {len(new_paths)} new entries to {LIST_FILE}")
    print(f"  Total training files: {total}")
    print()

if __name__ == '__main__':
    main()
