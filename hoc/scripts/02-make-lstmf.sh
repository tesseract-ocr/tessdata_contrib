#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 02-make-lstmf.sh
#
# Converts PNG+gt.txt pairs into .lstmf training files.
#
# Scans two directories:
#   rendered/       — synthetic images from render-corpus.py
#   scan-input/     — real scan images you supply (PNG + matching .gt.txt)
#
# Box file format: cluster-per-character (NOT WordStr).
# WordStr format stores "WordStr" as the transcription in the lstmf,
# causing "Can't encode transcription: 'WordStr'" errors in lstmtraining.
# Instead, each Warang Citi character gets its own equal-width x-slice box.
#
# Output:
#   lstmf/rendered/   — lstmf from synthetic images
#   lstmf/scan/       — lstmf from real scan images
#   lstmf/list.txt    — combined training file list
#
# Prerequisites:
#   Run 01-prep-base.sh first (needs tessdata_best/hoc_base.traineddata)
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT_LSTMF="$SCRIPT_DIR/lstmf"
RENDERED_DIR="$SCRIPT_DIR/rendered"
SCAN_DIR="$SCRIPT_DIR/scan-input"

[ -f "$TESSDATA_BEST/hoc_base.traineddata" ] || {
    echo "ERROR: tessdata_best/hoc_base.traineddata not found."
    echo "  Run ./01-prep-base.sh first."
    exit 1
}
[ -f "$TESSDATA_BEST/configs/lstm.train" ] || {
    echo "ERROR: tessdata_best/configs/lstm.train not found."
    exit 1
}

mkdir -p "$OUTPUT_LSTMF/rendered" "$OUTPUT_LSTMF/scan"
> "$OUTPUT_LSTMF/list.txt"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 2 — PNG+GT → lstmf"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

process_dir() {
    local src_dir="$1"
    local out_dir="$2"
    local label="$3"

    if [ ! -d "$src_dir" ]; then
        echo "  $label: directory not found, skipping"
        return
    fi

    local count
    count=$(find "$src_dir" -maxdepth 1 \( -name "*.png" -o -name "*.jpg" \
            -o -name "*.tif" -o -name "*.ppm" \) 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -eq 0 ]; then
        echo "  $label: no images found in $src_dir"
        return
    fi

    echo ""
    echo "→ Processing $label ($count images from $src_dir)..."

    # Run Python to create cluster-format box files and lstmf
    python3 - "$src_dir" "$out_dir" "$OUTPUT_LSTMF/list.txt" "$label" << 'PYEOF'
import sys, unicodedata, subprocess, shutil
from pathlib import Path
from PIL import Image

src_dir, out_dir, list_txt, label = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
TESSDATA_BEST = "tessdata_best"

def warang_citi_clusters(text):
    """Split Warang Citi text into character clusters.
    Warang Citi signs U+1C78-U+1C7D (category Lm) are modifiers that attach
    visually to the preceding letter — group them with it. All other chars
    (digits, letters, punct, space) are standalone clusters.
    """
    clusters, chars, i = [], list(text), 0
    while i < len(chars):
        c = chars[i]; cl = c; i += 1
        while i < len(chars) and unicodedata.category(chars[i]) in ('Lm', 'Mn', 'Mc', 'Cf'):
            cl += chars[i]; i += 1
        clusters.append(cl)
    return [c for c in clusters if c.strip()]

def make_lstmf(img_path, out_dir, list_file):
    img_path = Path(img_path)
    gt_path  = img_path.with_suffix('.gt.txt')
    if not img_path.exists() or not gt_path.exists():
        return False

    gt_text  = gt_path.read_text(encoding='utf-8').strip()
    clusters = warang_citi_clusters(gt_text)
    if not clusters:
        return False

    out_dir  = Path(out_dir)
    stem     = img_path.stem
    dst_png  = out_dir / (stem + '.png')
    box_path = out_dir / (stem + '.box')
    lstmf    = out_dir / (stem + '.lstmf')

    shutil.copy2(img_path, dst_png)
    img  = Image.open(dst_png)
    W, H = img.size
    n    = len(clusters)
    cw   = W / n
    # One equal-width x-slice per cluster — cluster format, NOT WordStr
    lines = [f"{c} {int(i*cw)} 0 {int((i+1)*cw)} {H} 0"
             for i, c in enumerate(clusters)]
    lines.append("\t 0 0 1 1 0")
    box_path.write_text("\n".join(lines) + "\n", encoding='utf-8')

    # PSM 7 (single line) → PSM 6 (block) → PSM 10 (single char) fallback
    for psm in ("7", "6", "10"):
        subprocess.run(
            ["tesseract", str(dst_png), str(out_dir / stem),
             "--tessdata-dir", TESSDATA_BEST,
             "--dpi", "300", "--psm", psm,
             "-l", "hoc_base", "lstm.train"],
            capture_output=True, text=True
        )
        if lstmf.exists():
            with open(list_file, 'a', encoding='utf-8') as lf:
                lf.write(str(lstmf) + '\n')
            return True

    dst_png.unlink(missing_ok=True)
    box_path.unlink(missing_ok=True)
    return False

imgs = sorted(
    [p for p in Path(src_dir).iterdir()
     if p.suffix.lower() in ('.png', '.jpg', '.tif', '.tiff', '.ppm')]
)
pass_n = fail_n = skip_n = 0
for img in imgs:
    gt = img.with_suffix('.gt.txt')
    if not gt.exists():
        skip_n += 1
        continue
    if make_lstmf(img, out_dir, list_txt):
        pass_n += 1
    else:
        fail_n += 1

print(f"  {label}: {pass_n} OK  {fail_n} failed  {skip_n} skipped (no gt.txt)")
PYEOF
}

process_dir "$RENDERED_DIR"  "$OUTPUT_LSTMF/rendered"  "Synthetic rendered"
process_dir "$SCAN_DIR"      "$OUTPUT_LSTMF/scan"      "Real scan images"

TOTAL=$(wc -l < "$OUTPUT_LSTMF/list.txt" | tr -d ' ')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done. lstmf/list.txt contains $TOTAL files."
echo ""
echo "  NEXT: caffeinate -i ./03-train.sh > training.log 2>&1 &"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
