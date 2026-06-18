#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 03-create-lstmf.sh
#
# PREVIOUS STEP: 02-extract-model.sh extracted output/ori.lstm
#   from the base traineddata. That file is not needed here,
#   but 01-generate-images.sh must have completed cleanly so
#   ground-truth/chapakala19.tif AND chapakala19.box both exist.
#
# WHAT THIS DOES:
#   Passes the multi-page TIFF and its .box ground-truth file
#   to Tesseract in lstm.train mode. Tesseract reads each page,
#   aligns it against the box file character-by-character, and
#   writes a single chapakala19.lstmf — a compact binary bundle
#   of (image region, expected text) pairs that lstmtraining
#   reads during Step 4.
#
#   NOTE: tessdata_best/configs/lstm.train must exist (the
#   config that tells Tesseract to write .lstmf output).
#   It was copied there from the system tessdata on first run.
#
# NEXT STEP: ./04-train.sh
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

GT_DIR="$SCRIPT_DIR/ground-truth"
LSTMF_DIR="$SCRIPT_DIR/lstmf"
TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"

# ── Preflight checks ─────────────────────────────────────────────
[ -f "$GT_DIR/chapakala19.tif" ] || {
  echo "ERROR: ground-truth/chapakala19.tif not found."
  echo "Run 01-generate-images.sh and let it finish completely."
  exit 1
}
[ -f "$GT_DIR/chapakala19.box" ] || {
  echo "ERROR: ground-truth/chapakala19.box not found."
  echo "The .box file is only written when text2image exits cleanly."
  echo "Re-run 01-generate-images.sh and wait for it to finish."
  exit 1
}
[ -f "$TESSDATA_BEST/ori.traineddata" ] || {
  echo "ERROR: tessdata_best/ori.traineddata not found. Run 00-setup.sh first."
  exit 1
}

TIF_SIZE=$(du -sh "$GT_DIR/chapakala19.tif" | cut -f1)
BOX_LINES=$(wc -l < "$GT_DIR/chapakala19.box" | tr -d ' ')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3 — Creating .lstmf training file"
echo "  TIFF:  $TIF_SIZE  ($GT_DIR/chapakala19.tif)"
echo "  Boxes: $BOX_LINES character entries"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Clear any previous lstmf output
rm -f "$LSTMF_DIR"/chapakala19.lstmf "$LSTMF_DIR/list.txt"

echo "→ Running tesseract lstm.train on the full TIFF..."
echo "  (This reads the .box file as ground truth and may take a few minutes)"
echo ""

# Tesseract reads chapakala19.tif page by page and uses chapakala19.box
# for character-level ground truth, producing a single .lstmf file.
tesseract \
  "$GT_DIR/chapakala19.tif" \
  "$LSTMF_DIR/chapakala19" \
  --tessdata-dir "$TESSDATA_BEST" \
  -l ori \
  --psm 6 \
  lstm.train \
  2>&1

[ -f "$LSTMF_DIR/chapakala19.lstmf" ] || {
  echo ""
  echo "ERROR: chapakala19.lstmf was not created. Check the output above."
  exit 1
}

# Write the list file — lstmtraining reads this to find training data
echo "$LSTMF_DIR/chapakala19.lstmf" > "$LSTMF_DIR/list.txt"

LSTMF_SIZE=$(du -sh "$LSTMF_DIR/chapakala19.lstmf" | cut -f1)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Created: lstmf/chapakala19.lstmf  ($LSTMF_SIZE)"
echo ""
echo "  NEXT STEP → ./04-train.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
