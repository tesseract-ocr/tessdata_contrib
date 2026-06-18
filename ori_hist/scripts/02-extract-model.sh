#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 02-extract-model.sh
#
# PREVIOUS STEP: 01-generate-images.sh rendered the corpus into
#   ground-truth/chapakala19.tif and chapakala19.box.
#   Both files must exist before continuing.
#
# WHAT THIS DOES:
#   Cracks open tessdata_best/ori.traineddata and pulls out the
#   raw LSTM neural network (ori.lstm). Fine-tuning starts from
#   this existing network so the model already understands Odia
#   script structure — we're only teaching it Chapakala 19's
#   specific letterform shapes.
#
# NEXT STEP: ./03-create-lstmf.sh
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"

[ -f "$TESSDATA_BEST/ori.traineddata" ] || { echo "ERROR: tessdata_best/ori.traineddata not found. Run 00-setup.sh first."; exit 1; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 2 — Extracting LSTM from ori.traineddata"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Pull the raw LSTM network out of the tessdata bundle
combine_tessdata -e "$TESSDATA_BEST/ori.traineddata" "$OUTPUT/ori.lstm"

ls -lh "$OUTPUT/ori.lstm"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Extracted: output/ori.lstm"
echo ""
echo "  NEXT STEP → ./03-create-lstmf.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
