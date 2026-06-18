#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 05-package.sh
#
# Turns the trained LSTM checkpoint into a .traineddata file
# that Tesseract can actually use.
#
# Output:
#   output/ori_histv2.traineddata  — the finished model
#
# To use it anywhere on your Mac:
#   cp output/ori_histv2.traineddata /opt/homebrew/share/tessdata/
#   tesseract myimage.tif output -l ori_histv2
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
MODEL_NAME="ori_histv2"

[ -f "$OUTPUT/${MODEL_NAME}_checkpoint" ] || {
  echo "ERROR: output/${MODEL_NAME}_checkpoint not found."
  echo "Run 04-train.sh first."
  exit 1
}

# Prefer the best named checkpoint (lowest BCER, second field of filename),
# falling back to the rolling ori_histv2_checkpoint if none exist.
# Also search chapakala19_ prefix for backward compat with Run 11 checkpoints
BEST_CHECKPOINT=$(ls "$OUTPUT"/${MODEL_NAME}_*.checkpoint "$OUTPUT"/chapakala19_*.checkpoint 2>/dev/null | \
  grep -v '_checkpoint$' | sort -t_ -k2 -n | head -1)
if [ -n "$BEST_CHECKPOINT" ]; then
  PACKAGE_FROM="$BEST_CHECKPOINT"
else
  PACKAGE_FROM="$OUTPUT/${MODEL_NAME}_checkpoint"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 5 — Packaging model"
echo "  Source: $(basename $PACKAGE_FROM)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step A: Convert checkpoint → raw .lstm file
lstmtraining \
  --stop_training \
  --continue_from    "$PACKAGE_FROM" \
  --traineddata      "$TESSDATA_BEST/ori.traineddata" \
  --model_output     "$OUTPUT/${MODEL_NAME}.lstm"

# Tesseract 5.5.x on macOS prepends a ~196-byte corrupt header (containing
# raw heap pointers) to the lstmtraining --stop_training output.  Strip it.
# The real LSTMRecognizer data always starts with a \x00 byte followed by
# \x06\x00\x00\x00Series (the network name).
python3 - "$OUTPUT/${MODEL_NAME}.lstm" << 'PYEOF'
import sys, os
path = sys.argv[1]
data = open(path, 'rb').read()
needle = b'\x00\x06\x00\x00\x00Series'
idx = data.find(needle)
if idx > 0:
    print(f"  Stripping {idx}-byte corrupt header from {os.path.basename(path)}")
    open(path, 'wb').write(data[idx:])
else:
    print("  .lstm header looks clean — no stripping needed")
PYEOF

echo "→ Extracted LSTM weights to output/${MODEL_NAME}.lstm"

# Step B: Bundle the .lstm into a .traineddata file.
#   combine_tessdata -o modifies a traineddata IN PLACE — it doesn't
#   take a base file as an argument.  So we first copy ori.traineddata
#   under the new name, then replace only the LSTM component inside it.
cp "$TESSDATA_BEST/ori.traineddata" "$OUTPUT/${MODEL_NAME}.traineddata"
combine_tessdata \
  -o "$OUTPUT/${MODEL_NAME}.traineddata" \
  "$OUTPUT/${MODEL_NAME}.lstm"

ls -lh "$OUTPUT/${MODEL_NAME}.traineddata"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Model ready: output/${MODEL_NAME}.traineddata"
echo ""
echo "  NEXT STEP → ./06-test.sh  (check how well it reads)"
echo ""
echo "  To install system-wide:"
echo "  cp output/${MODEL_NAME}.traineddata /opt/homebrew/share/tessdata/"
echo "  tesseract your-scan.tif result -l ${MODEL_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
