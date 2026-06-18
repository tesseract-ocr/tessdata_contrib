#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 00-setup.sh — Run this ONCE before anything else.
#
# PREVIOUS STEP: nothing — this is the starting point.
#
# WHAT THIS DOES:
#   Installs GNU Make 4+, clones tesstrain, downloads the base
#   ori.traineddata model, downloads the initial Odia corpus, and
#   verifies the font is visible to text2image.
#
# NEXT STEP: build or review corpus/ori.training_text, then run
#   ./01-generate-images.sh
# ═══════════════════════════════════════════════════════════════
set -e  # stop immediately if any command fails

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Tesseract Odia Training — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. GNU Make 4+ (needed by tesstrain) ────────────────────
if gmake --version 2>/dev/null | grep -q "GNU Make [4-9]"; then
  echo "✓ gmake (GNU Make 4+) already installed"
else
  echo "→ Installing GNU Make 4 via Homebrew (needed for tesstrain)..."
  brew install make
  echo "  Done. Use 'gmake' instead of 'make' in these scripts."
fi

# ── 2. Clone tesstrain (official Tesseract training framework) ──
if [ -d "tesstrain/.git" ]; then
  echo "✓ tesstrain already cloned"
else
  echo "→ Cloning tesstrain..."
  git clone --depth 1 https://github.com/tesseract-ocr/tesstrain.git
fi

# ── 3. Download ori.traineddata (best quality, for fine-tuning) ─
if [ -f "tessdata_best/ori.traineddata" ]; then
  echo "✓ ori.traineddata already downloaded"
else
  echo "→ Downloading ori.traineddata from tessdata_best (~6 MB)..."
  curl -L --progress-bar \
    -o tessdata_best/ori.traineddata \
    "https://github.com/tesseract-ocr/tessdata_best/raw/main/ori.traineddata"
fi

# ── 4. Download Odia training corpus ───────────────────────────
if [ -f "corpus/ori.training_text" ]; then
  echo "✓ Odia training corpus already downloaded"
else
  echo "→ Downloading Odia training corpus from langdata_lstm..."
  curl -L --progress-bar \
    -o corpus/ori.training_text \
    "https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/main/ori/ori.training_text"
fi

# ── 5. Verify font ──────────────────────────────────────────────
if [ -f "fonts/Chapakala19Regular.ttf" ]; then
  echo "✓ Chapakala19Regular.ttf is in fonts/"
else
  echo "✗ Font not found at fonts/Chapakala19Regular.ttf"
  echo "  Please copy the font file into the fonts/ folder."
  exit 1
fi

# ── 6. Verify font name is visible to text2image ───────────────
FONT_CHECK=$(text2image --list_available_fonts --fonts_dir "$SCRIPT_DIR/fonts" 2>&1 | grep -i "Chapakala19" || true)
if [ -n "$FONT_CHECK" ]; then
  echo "✓ Font recognised by text2image as: Chapakala19"
else
  echo "✗ text2image cannot see the font. Check the file in fonts/ folder."
  exit 1
fi

# ── Summary ─────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Setup complete! Your training folder is ready."
echo ""
echo "  Corpus lines: $(wc -l < corpus/ori.training_text | tr -d ' ')"
echo "  Font:         fonts/Chapakala19Regular.ttf"
echo "  Base model:   tessdata_best/ori.traineddata"
echo ""
echo "  NEXT STEP → open corpus/ori.training_text"
echo "  Add any Odia text you want, then run:"
echo "  ./01-generate-images.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
