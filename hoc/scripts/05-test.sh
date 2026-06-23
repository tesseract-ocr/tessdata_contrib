#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 05-test.sh — Quick OCR test on a single image.
#
# Usage:
#   ./05-test.sh <image> [ground-truth.txt]
#
# Example:
#   ./05-test.sh test-images/sample.png test-images/sample.gt.txt
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

IMAGE="${1:-}"
GT="${2:-}"

[ -n "$IMAGE" ] || { echo "Usage: $0 <image> [ground-truth.txt]"; exit 1; }
[ -f "$IMAGE" ] || { echo "ERROR: image not found: $IMAGE"; exit 1; }

SYSTEM_TESSDATA="/opt/homebrew/share/tessdata"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  OCR test: $(basename $IMAGE)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for model in hoc_v1 sat_indicocr; do
    if [ -f "$SYSTEM_TESSDATA/${model}.traineddata" ]; then
        oem=1
        [ "$model" = "sat_indicocr" ] && oem=0
        echo "── $model (oem $oem) ──"
        tesseract "$IMAGE" stdout \
            --tessdata-dir "$SYSTEM_TESSDATA" \
            -l "$model" --psm 7 --oem "$oem" 2>/dev/null || echo "(no output)"
    else
        echo "── $model: not installed ──"
    fi
done

if [ -n "$GT" ] && [ -f "$GT" ]; then
    echo ""
    echo "── Ground truth ──"
    cat "$GT"
fi
echo ""
