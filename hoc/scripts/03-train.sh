#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 03-train.sh
#
# Trains the Ho (Warang Citi) LSTM model FROM SCRATCH.
#
# There is no existing LSTM model for Ho/Warang Citi, so we
# train from scratch using --net_spec to define the network.
#
# NOTE: From-scratch training needs substantial data (ideally
# 1000+ training lines). With less data, the model will plateau
# early. The Santali project showed that <500 lines plateaued
# at ~42% accuracy from scratch, but fine-tuning from a base
# model worked with that data volume.
#
# Network spec for Warang Citi:
#   - Input: 1 channel, 36px height, variable width
#   - Ct3,3,16: 3×3 convolution, 16 filters
#   - Mp3,3: 3×3 max pooling
#   - Lfys48: LSTM 48 units, y-scan, with summary
#   - Lfx96: LSTM 96 units, forward x-scan
#   - Lrx96: LSTM 96 units, reverse x-scan
#   - Lfx192: LSTM 192 units, forward x-scan
#   - O1c109: Output layer, 1D, 109 classes (108 chars + CTC blank)
#
# Checkpoints saved every 100 iterations.
# Safe to stop with Ctrl+C — resumes from latest checkpoint.
#
# Usage:
#   caffeinate -i ./03-train.sh > logs/training.log 2>&1 &
#   tail -f logs/training.log
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
LSTMF_DIR="$SCRIPT_DIR/lstmf"
MODEL_NAME="hoc_v1"

TRAIN_LIST="$LSTMF_DIR/list.txt"
[ -f "$TRAIN_LIST" ] || { echo "ERROR: $TRAIN_LIST not found. Run 02-make-lstmf.sh first."; exit 1; }
LSTMF_COUNT=$(wc -l < "$TRAIN_LIST" | tr -d ' ')
[ "$LSTMF_COUNT" -gt 0 ] || { echo "ERROR: $TRAIN_LIST is empty."; exit 1; }

MAX_ITERATIONS=400000
LEARNING_RATE=0.01
NET_SPEC="[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx192 O1c80]"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3 — LSTM Training FROM SCRATCH (Ho / Warang Citi)"
echo "  Network:        $NET_SPEC"
echo "  Training data:  $LSTMF_COUNT .lstmf files"
echo "  Iterations:     $MAX_ITERATIONS max"
echo "  Learning rate:  $LEARNING_RATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for existing checkpoint to resume from
if [ -f "$OUTPUT/${MODEL_NAME}_checkpoint" ]; then
    echo "→ Resuming from existing checkpoint"
    lstmtraining \
        --continue_from      "$OUTPUT/${MODEL_NAME}_checkpoint" \
        --model_output       "$OUTPUT/$MODEL_NAME" \
        --traineddata        "$TESSDATA_BEST/hoc_base.traineddata" \
        --train_listfile     "$TRAIN_LIST" \
        --learning_rate      "$LEARNING_RATE" \
        --max_iterations     "$MAX_ITERATIONS" \
        --target_error_rate  -1
else
    echo "→ Starting fresh from scratch (no base model)"
    lstmtraining \
        --model_output       "$OUTPUT/$MODEL_NAME" \
        --traineddata        "$TESSDATA_BEST/hoc_base.traineddata" \
        --net_spec           "$NET_SPEC" \
        --train_listfile     "$TRAIN_LIST" \
        --learning_rate      "$LEARNING_RATE" \
        --max_iterations     "$MAX_ITERATIONS" \
        --target_error_rate  -1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Training done. NEXT: ./04-package.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
