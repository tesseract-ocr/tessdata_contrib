#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 01-prep-base.sh
#
# Creates hoc_base.traineddata from the Warang Citi unicharset.
# This is the target traineddata that defines the character set
# the LSTM model will learn to recognise.
#
# Usage:
#   ./01-prep-base.sh
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"

[ -f "$OUTPUT/hoc.unicharset" ] || { echo "ERROR: output/hoc.unicharset not found."; exit 1; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1 — Prepare base traineddata (Ho / Warang Citi)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

combine_lang_model \
    --input_unicharset "$OUTPUT/hoc.unicharset" \
    --script_dir "$TESSDATA_BEST" \
    --output_dir "$TESSDATA_BEST" \
    --lang hoc_base

echo ""
echo "  Created: tessdata_best/hoc_base.traineddata"
echo ""

# Also copy the Warang Citi unicharset alongside
cp "$OUTPUT/hoc.unicharset" "$TESSDATA_BEST/hoc.unicharset"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done. NEXT: render corpus → ./render-corpus.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
