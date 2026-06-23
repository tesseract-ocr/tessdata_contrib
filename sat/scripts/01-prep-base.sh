#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 01-prep-base.sh
#
# One-time setup for Santali LSTM training.
#
# What this does:
#   A. Downloads tessdata_best/ori.traineddata (LSTM base for fine-tuning)
#   B. Extracts output/ori.lstm (the raw LSTM weights)
#   C. Creates output/sat.unicharset (full Ol Chiki block + punctuation)
#   D. Builds tessdata_best/sat_base.traineddata via combine_lang_model
#      (this traineddata is used ONLY for encoding GT during lstmf creation
#       and as the --traineddata argument for lstmtraining)
#
# Why fine-tune from ori.traineddata?
#   No LSTM model exists for Santali/Ol Chiki — not in tessdata_best,
#   tessdata, or tessdata_contrib. The indic-ocr sat model is legacy (Pre-4.0.0)
#   with no LSTM weights. Fine-tuning from ori gives a well-trained LSTM
#   starting point; the output layer is completely rebuilt for Ol Chiki.
#   Expect BCER to start ~50% (output layer rebuild) then drop rapidly.
#
# Run once before any training. Safe to re-run.
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
SYSTEM_TESSDATA="/opt/homebrew/share/tessdata"

mkdir -p "$TESSDATA_BEST" "$OUTPUT"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1 — Santali training setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── A: Download ori LSTM base ──────────────────────────────────
echo ""
echo "→ [A] Base model..."
if [ ! -f "$TESSDATA_BEST/ori.traineddata" ]; then
    echo "  Downloading tessdata_best/ori.traineddata..."
    curl -fL --progress-bar \
        "https://github.com/tesseract-ocr/tessdata_best/raw/main/ori.traineddata" \
        -o "$TESSDATA_BEST/ori.traineddata"
    echo "  Downloaded: $(du -h $TESSDATA_BEST/ori.traineddata | cut -f1)"
else
    echo "  Already present: tessdata_best/ori.traineddata"
fi

# ── B: Extract LSTM weights ────────────────────────────────────
echo ""
echo "→ [B] Extracting ori.lstm..."
combine_tessdata -e "$TESSDATA_BEST/ori.traineddata" "$OUTPUT/ori.lstm" 2>/dev/null
ls -lh "$OUTPUT/ori.lstm"
echo "  (This is the starting point for fine-tuning)"

# ── C: Create Santali unicharset ───────────────────────────────
echo ""
echo "→ [C] Building Santali unicharset (Ol Chiki + punctuation)..."

python3 << 'PYEOF'
from pathlib import Path

# Full Ol Chiki Unicode block U+1C50–U+1C7F
# U+1C50-1C59: Digits (property 0 — not IsAlpha)
# U+1C5A-1C77: Letters (property 1 — IsAlpha)
# U+1C78-1C7D: Signs/modifiers (property 0)
# U+1C7E-1C7F: Punctuation (property 10)
# Plus common ASCII punct used alongside Ol Chiki text

entries = [
    # (char, props, direction, script, type_suffix)
]

# Ol Chiki digits
for cp in range(0x1C50, 0x1C5A):
    entries.append((chr(cp), '0', '0', 'Ol_Chiki', 'x'))

# Ol Chiki letters
for cp in range(0x1C5A, 0x1C78):
    entries.append((chr(cp), '1', '0', 'Ol_Chiki', 'x'))

# Ol Chiki signs / modifiers
for cp in range(0x1C78, 0x1C7E):
    entries.append((chr(cp), '0', '0', 'Ol_Chiki', ''))

# Ol Chiki punctuation
for cp in range(0x1C7E, 0x1C80):
    entries.append((chr(cp), '10', '10', 'Ol_Chiki', 'p'))

# Common ASCII punctuation that appears in Santali texts
ascii_punct = [
    ('.', '10', '10', 'Common', 'p'),
    (',', '10', '10', 'Common', 'p'),
    (':', '10', '10', 'Common', 'p'),
    ('?', '10', '10', 'Common', 'p'),
    ('!', '10', '10', 'Common', 'p'),
    ('-', '10', '10', 'Common', 'p'),
    ('/', '10', '10', 'Common', 'p'),
    ('"', '10', '10', 'Common', 'p'),
    ("'", '10', '10', 'Common', 'p'),
    ('(', '10', '10', 'Common', 'p'),
    (')', '10', '10', 'Common', 'p'),
    ('*', '10', '10', 'Common', 'p'),
    ('%', '10', '10', 'Common', 'p'),
]
entries.extend(ascii_punct)

# ASCII digits
for ch in '0123456789':
    entries.append((ch, '0', '0', 'Common', 'x'))

uid = 3  # 0=NULL, 1=Joined, 2=Broken
lines = [f'{len(entries) + 3}\n']  # count line (updated below)
lines.append('NULL 0 NULL 0\n')
lines.append('Joined 7 0,69,188,255,486,1218,0,30,486,1188 Latin 1 0 1 Joined\t# Joined [4a 6f 69 6e 65 64 ]a\n')
lines.append('|Broken|0|1 f 0,69,186,255,892,2138,0,80,892,2058 Common 2 10 2 |Broken|0|1\t# Broken\n')

for char, props, direction, script, type_sfx in entries:
    hex_cp = ' '.join(f'{ord(c):x}' for c in char)
    comment_type = f' ]{type_sfx}' if type_sfx else ' ]'
    line = (f'{char} {props} 0,255,0,255,0,0,0,0,0,0 {script}'
            f' {uid} {direction} {uid} {char}\t'
            f'# {char} [{hex_cp}{comment_type}\n')
    lines.append(line)
    uid += 1

# Patch the count
lines[0] = f'{uid}\n'

out = Path('output/sat.unicharset')
out.write_text(''.join(lines), encoding='utf-8')
print(f'  {uid} entries in unicharset → output/sat.unicharset')
print(f'  Ol Chiki: 10 digits + 30 letters + 6 signs + 2 punct = 48')
print(f'  ASCII punct: {len(ascii_punct)}  ASCII digits: 10')
PYEOF

# ── D: Build sat_base.traineddata ─────────────────────────────
echo ""
echo "→ [D] Building tessdata_best/sat_base.traineddata..."

LANGMODEL_OUT="output/langmodel_tmp"
mkdir -p "$LANGMODEL_OUT"

# combine_lang_model needs radical-stroke.txt (for CJK) — create a dummy if absent
if [ ! -f "$SYSTEM_TESSDATA/radical-stroke.txt" ]; then
    printf "0\n" > "$SYSTEM_TESSDATA/radical-stroke.txt"
    echo "  Created dummy radical-stroke.txt"
fi

mkdir -p "$SYSTEM_TESSDATA/sat_base"
touch "$SYSTEM_TESSDATA/sat_base/sat_base.config"

build_ok=0

if combine_lang_model \
       --input_unicharset output/sat.unicharset \
       --script_dir "$SYSTEM_TESSDATA" \
       --output_dir "$LANGMODEL_OUT" \
       --lang sat_base 2>/dev/null; then
    echo "  Built with compressed recoder."
    build_ok=1
fi

if [ "$build_ok" -eq 0 ]; then
    echo "  Trying --pass_through_recoder..."
    if combine_lang_model \
           --input_unicharset output/sat.unicharset \
           --script_dir "$SYSTEM_TESSDATA" \
           --output_dir "$LANGMODEL_OUT" \
           --lang sat_base \
           --pass_through_recoder 2>&1 | grep -v "^Warning\|^Failed\|^Config"; then
        echo "  Built with pass-through recoder."
        build_ok=1
    fi
fi

[ "$build_ok" -eq 1 ] || { echo "ERROR: combine_lang_model failed."; exit 1; }

BUILT="$LANGMODEL_OUT/sat_base/sat_base.traineddata"
[ -f "$BUILT" ] || { echo "ERROR: expected $BUILT not created."; exit 1; }

cp "$BUILT" "$TESSDATA_BEST/sat_base.traineddata"
ls -lh "$TESSDATA_BEST/sat_base.traineddata"

# Verify the unicharset is inside
combine_tessdata -u "$TESSDATA_BEST/sat_base.traineddata" /tmp/sat_base_verify 2>/dev/null
UC_COUNT=$(head -1 /tmp/sat_base_verify.lstm-unicharset | tr -d ' ')
echo "  Unicharset entries in sat_base.traineddata: $UC_COUNT"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Setup complete."
echo ""
echo "  Base model:           tessdata_best/ori.traineddata"
echo "  LSTM weights:         output/ori.lstm"
echo "  Santali unicharset:   output/sat.unicharset ($UC_COUNT entries)"
echo "  Training traineddata: tessdata_best/sat_base.traineddata"
echo ""
echo "  NEXT STEPS:"
echo "    1. python3 render-corpus.py       (renders synthetic images)"
echo "    2. ./02-make-lstmf.sh             (creates .lstmf training files)"
echo "    3. caffeinate -i ./03-train.sh    (starts training)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
