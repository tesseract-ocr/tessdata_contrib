#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 04-package.sh
#
# Packages the best training checkpoint into a usable .traineddata.
#
# IMPORTANT — checkpoint selection:
#   The script picks the checkpoint with the LOWEST BCER (second field
#   of the filename, e.g. sat_v1_2.341_4500_18200.checkpoint → 2.341%).
#   Review the training log to confirm this is the intended best.
#   To override, set: export BEST_CHECKPOINT=/path/to/specific.checkpoint
#
# Output:
#   output/sat_v1.traineddata
#
# To install:
#   cp output/sat_v1.traineddata /opt/homebrew/share/tessdata/
#   tesseract myimage.tif result -l sat_v1
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
MODEL_NAME="sat_v1"

[ -f "$OUTPUT/${MODEL_NAME}_checkpoint" ] || {
    echo "ERROR: output/${MODEL_NAME}_checkpoint not found."
    echo "  Run 03-train.sh first."
    exit 1
}

if [ -z "$BEST_CHECKPOINT" ]; then
    BEST_CHECKPOINT=$(ls "$OUTPUT"/${MODEL_NAME}_*.checkpoint 2>/dev/null | \
        grep -v '_checkpoint$' | sort -t_ -k2 -n | head -1)
fi

[ -n "$BEST_CHECKPOINT" ] || BEST_CHECKPOINT="$OUTPUT/${MODEL_NAME}_checkpoint"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 4 — Packaging model"
echo "  Source: $(basename $BEST_CHECKPOINT)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

lstmtraining \
    --stop_training \
    --continue_from    "$BEST_CHECKPOINT" \
    --traineddata      "$TESSDATA_BEST/sat_base.traineddata" \
    --old_traineddata  "$TESSDATA_BEST/ori.traineddata" \
    --model_output     "$OUTPUT/${MODEL_NAME}.lstm"

# Strip Tesseract 5.5.x macOS corrupt header (if present)
python3 - "$OUTPUT/${MODEL_NAME}.lstm" << 'PYEOF'
import sys, os
path = sys.argv[1]
data = open(path, 'rb').read()
needle = b'\x00\x06\x00\x00\x00Series'
idx = data.find(needle)
if idx > 0:
    print(f"  Stripping {idx}-byte corrupt header")
    open(path, 'wb').write(data[idx:])
else:
    print("  .lstm header clean — no stripping needed")
PYEOF

# Bundle into traineddata (start from sat_base — preserves Santali unicharset)
cp "$TESSDATA_BEST/sat_base.traineddata" "$OUTPUT/${MODEL_NAME}.traineddata"
combine_tessdata \
    -o "$OUTPUT/${MODEL_NAME}.traineddata" \
    "$OUTPUT/${MODEL_NAME}.lstm"

ls -lh "$OUTPUT/${MODEL_NAME}.traineddata"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Model ready: output/${MODEL_NAME}.traineddata"
echo ""
echo "  To install:"
echo "  cp output/${MODEL_NAME}.traineddata /opt/homebrew/share/tessdata/"
echo "  tesseract your-scan.tif result -l ${MODEL_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
