#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 03-train-finetune.sh
#
# Fine-tunes the Ho (Warang Citi) LSTM model from Latin base.
#
# The LSTM output layer is completely rebuilt for the Ho/PUA
# unicharset. Conv layers and LSTM recurrent weights transfer
# from Latin — they learned generic text features (edges,
# strokes, spacing) that help even for a different script.
#
# This is the same approach that worked for Santali/Ol Chiki.
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
LSTMF_DIR="$SCRIPT_DIR/lstmf"
MODEL_NAME="hoc_v1"

TRAIN_LIST="$LSTMF_DIR/list.txt"
[ -f "$TRAIN_LIST" ] || { echo "ERROR: $TRAIN_LIST not found."; exit 1; }
LSTMF_COUNT=$(wc -l < "$TRAIN_LIST" | tr -d ' ')
[ "$LSTMF_COUNT" -gt 0 ] || { echo "ERROR: $TRAIN_LIST is empty."; exit 1; }

MAX_ITERATIONS=400000
LEARNING_RATE=0.001

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3 — LSTM Fine-tuning from Latin (Ho / Warang Citi)"
echo "  Base:           output/latin.lstm"
echo "  Training data:  $LSTMF_COUNT .lstmf files"
echo "  Iterations:     $MAX_ITERATIONS max"
echo "  Learning rate:  $LEARNING_RATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Checkpoint selection — resume from most recent if available
if [ -z "$CONTINUE_FROM" ]; then
    if [ -f "$OUTPUT/${MODEL_NAME}_checkpoint" ]; then
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
    --traineddata        "$TESSDATA_BEST/hoc_base.traineddata" \
    --train_listfile     "$TRAIN_LIST" \
    --learning_rate      "$LEARNING_RATE" \
    --net_mode           16 \
    --max_iterations     "$MAX_ITERATIONS" \
    --target_error_rate  -1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Training done. NEXT: ./04-package.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
