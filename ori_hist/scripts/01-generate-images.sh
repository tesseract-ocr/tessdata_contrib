#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 01-generate-images.sh
#
# PREVIOUS STEP: 00-setup.sh installed tools and downloaded the
#   base model. corpus/ori.training_text must exist (build it
#   with corpus/build-quality-corpus.py if starting fresh).
#
# WHAT THIS DOES:
#   Renders your Odia training corpus using Chapakala 19 into
#   a single multi-page TIFF + a .box ground-truth file.
#   text2image writes the .box file ONLY when it exits cleanly —
#   never kill this script mid-run.
#
# NEXT STEP: ./02-extract-model.sh
#
# Usage:
#   ./01-generate-images.sh          — use default LINE_LIMIT (see below)
#   ./01-generate-images.sh 10000    — render first 10 000 lines
#   ./01-generate-images.sh 0        — render the entire corpus (all lines)
#
# Output (in ground-truth/):
#   chapakala19.NNNN.tif    — one TIFF per rendered page
#   chapakala19.NNNN.gt.txt — the exact text on that page
#
# Run again any time you change the corpus or font settings.
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

FONT_DIR="$SCRIPT_DIR/fonts"
CORPUS="$SCRIPT_DIR/corpus/ori.training_text"
OUT_DIR="$SCRIPT_DIR/ground-truth"
FONT_NAME="Chapakala19"

# ── How many lines to render ─────────────────────────────────────
# Pass a number as the first argument, or change the default here.
# 0 means "all lines in the corpus".
LINE_LIMIT="${1:-10000}"

# ── Preflight checks ─────────────────────────────────────────────
[ -f "$CORPUS" ]                          || { echo "ERROR: corpus/ori.training_text not found. Run 00-setup.sh first."; exit 1; }
[ -f "$FONT_DIR/Chapakala19Regular.ttf" ] || { echo "ERROR: fonts/Chapakala19Regular.ttf not found."; exit 1; }

TOTAL_LINES=$(wc -l < "$CORPUS" | tr -d ' ')

# Build the text file to pass to text2image
RENDER_CORPUS="$CORPUS"
if [ "$LINE_LIMIT" -gt 0 ] && [ "$LINE_LIMIT" -lt "$TOTAL_LINES" ]; then
  RENDER_CORPUS="/tmp/chapakala19_render_subset.txt"
  head -"$LINE_LIMIT" "$CORPUS" > "$RENDER_CORPUS"
  LINES_USED="$LINE_LIMIT (of $TOTAL_LINES total)"
else
  LINES_USED="$TOTAL_LINES (full corpus)"
  LINE_LIMIT=0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1 — Generating training images"
echo "  Font:   $FONT_NAME"
echo "  Lines:  $LINES_USED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Clear old ground-truth files so we start fresh
rm -f "$OUT_DIR"/chapakala19.*

# ── Run text2image ───────────────────────────────────────────────
# What each flag does:
#   --fonts_dir      where to find the font file
#   --font           exact name as fontconfig sees it
#   --text           corpus file — every line becomes a training example
#   --outputbase     prefix for output files
#   --max_pages 0    render all lines (0 = no limit)
#   --strip_unrenderable_words  skip words the font can't draw
#   --leading        extra space between lines (px)
#   --xsize          image width in pixels (wide = fewer line wraps)
#   --ysize          image height per line in pixels
#   --char_spacing   spacing multiplier between characters
#   --resolution     DPI — 300 matches real document scans
#   --ptsize         font size in points
#   --degrade_image  adds letterpress-like noise/blur (set true to enable)
#   --rotate_image   slight random tilt per line (set true to enable)

text2image \
  --fonts_dir      "$FONT_DIR" \
  --font           "$FONT_NAME" \
  --text           "$RENDER_CORPUS" \
  --outputbase     "$OUT_DIR/chapakala19" \
  --max_pages      0 \
  --strip_unrenderable_words \
  --leading        32 \
  --xsize          3600 \
  --ysize          480 \
  --char_spacing   1.0 \
  --resolution     300 \
  --ptsize         32 \
  --degrade_image  true \
  --rotate_image   true \
  2>&1

# Clean up temp subset file if we created one
[ "$RENDER_CORPUS" = "/tmp/chapakala19_render_subset.txt" ] && rm -f "$RENDER_CORPUS"

# ── Count output files ───────────────────────────────────────────
TIFF_COUNT=$(ls "$OUT_DIR"/chapakala19.*.tif 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Generated $TIFF_COUNT training image(s) in ground-truth/"
echo "  Lines rendered: $LINES_USED"
echo ""
echo "  TIP: Open a few .tif files in Preview to check they"
echo "  look right before training."
echo ""
echo "  To render more lines later:"
echo "  ./01-generate-images.sh 50000"
echo "  ./01-generate-images.sh 0      (full corpus)"
echo ""
echo "  NEXT STEP → ./02-extract-model.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
