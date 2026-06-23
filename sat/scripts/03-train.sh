#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 03-train.sh
#
# Fine-tunes the Santali LSTM model from ori (Odia) base weights.
#
# Because there is no existing LSTM model for Santali/Ol Chiki,
# we use ori.traineddata as the starting point. The LSTM output
# layer is completely rebuilt for the Santali unicharset.
#
# What to expect:
#   Iters   0–500:   BCER ~50% (output layer rebuild — normal)
#   Iters 500–2000:  BCER drops rapidly as Ol Chiki shapes are learned
#   Iters 2000+:     Steady improvement toward 1–5% range
#   Plateau:         Stop when BCER shows no new best for ~5,000 iters
#
# Checkpoints saved every 100 iterations.
# Safe to stop with Ctrl+C — resumes from latest checkpoint.
#
# Usage:
#   caffeinate -i ./03-train.sh > training.log 2>&1 &
#   tail -f training.log
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
LSTMF_DIR="$SCRIPT_DIR/lstmf"
MODEL_NAME="sat_v1"

[ -f "$LSTMF_DIR/list.txt" ] || { echo "ERROR: lstmf/list.txt not found. Run 02-make-lstmf.sh first."; exit 1; }
LSTMF_COUNT=$(wc -l < "$LSTMF_DIR/list.txt" | tr -d ' ')
[ "$LSTMF_COUNT" -gt 0 ] || { echo "ERROR: lstmf/list.txt is empty."; exit 1; }

MAX_ITERATIONS=400000
LEARNING_RATE=0.001

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3 — LSTM Fine-tuning (Santali / Ol Chiki)"
echo "  Base:           output/latin.lstm (fine-tuned from Latin)"
echo "  Training data:  $LSTMF_COUNT .lstmf files"
echo "  Iterations:     $MAX_ITERATIONS max"
echo "  Learning rate:  $LEARNING_RATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Checkpoint selection — resume from most recent checkpoint if available
# Otherwise start from ori.lstm (the initial base)
if [ -z "$CONTINUE_FROM" ]; then
    RECENT=$(ls "$OUTPUT"/${MODEL_NAME}_*.checkpoint 2>/dev/null | \
             grep -v '_checkpoint$' | sort -t_ -k4 -n | tail -1)
    if [ -n "$RECENT" ]; then
        CONTINUE_FROM="$RECENT"
        echo "→ Resuming from: $(basename $CONTINUE_FROM)"
    elif [ -f "$OUTPUT/${MODEL_NAME}_checkpoint" ]; then
        CONTINUE_FROM="$OUTPUT/${MODEL_NAME}_checkpoint"
        echo "→ Resuming from rolling checkpoint"
    else
        CONTINUE_FROM="$OUTPUT/latin.lstm"
        echo "→ Starting fresh from latin.lstm (first run)"
    fi
else
    echo "→ Using explicit checkpoint: $(basename $CONTINUE_FROM)"
fi

echo ""

lstmtraining \
    --continue_from      "$CONTINUE_FROM" \
    --old_traineddata    "$TESSDATA_BEST/Latin.traineddata" \
    --model_output       "$OUTPUT/$MODEL_NAME" \
    --traineddata        "$TESSDATA_BEST/sat_base.traineddata" \
    --train_listfile     "$LSTMF_DIR/list_run7.txt" \
    --learning_rate      "$LEARNING_RATE" \
    --net_mode           16 \
    --max_iterations     "$MAX_ITERATIONS" \
    --target_error_rate  -1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Training done. NEXT: ./04-package.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
