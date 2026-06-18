#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 04-train.sh
#
# Fine-tunes the Odia LSTM model on Chapakala 19.
#
# What "fine-tuning" means:
#   The existing ori model already knows Odia script structure,
#   Unicode mappings, and conjunct shaping. We show it thousands
#   of Chapakala 19 training lines so it learns this font's
#   specific stroke shapes, without forgetting general Odia.
#
# How long this takes (on CPU):
#   10 000 iterations  →  ~2–4 hours   (good first test)
#   50 000 iterations  →  ~12–24 hours  (production quality)
#   You can stop and resume at any time — checkpoints are saved.
#
# Output (in output/):
#   ori_histv2_checkpoint  — saved every 100 iterations
#   ori_histv2.traineddata — final packaged model (after 05-package.sh)
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TESSDATA_BEST="$SCRIPT_DIR/tessdata_best"
OUTPUT="$SCRIPT_DIR/output"
LSTMF_DIR="$SCRIPT_DIR/lstmf"

# Override --traineddata for unicharset-expansion runs (e.g. Run 10+):
#   export TRAINEDDATA=output/ori_expanded.traineddata
#   export OLD_TRAINEDDATA=tessdata_best/ori.traineddata   # required when unicharset changes
TRAINEDDATA="${TRAINEDDATA:-$TESSDATA_BEST/ori.traineddata}"
OLD_TRAINEDDATA="${OLD_TRAINEDDATA:-}"

# ── Configuration ───────────────────────────────────────────────
# Start small (10 000) for your first run to verify everything
# works, then increase for the real training run.
MAX_ITERATIONS=400000

# Learning rate: lower = more conservative, takes longer but safer.
# 0.001 is standard for fine-tuning from an existing model.
LEARNING_RATE=0.001

# ── Preflight checks ────────────────────────────────────────────
[ -f "$OUTPUT/ori.lstm" ]        || { echo "ERROR: output/ori.lstm not found. Run 02-extract-model.sh first."; exit 1; }
[ -f "$LSTMF_DIR/list.txt" ]     || { echo "ERROR: lstmf/list.txt not found. Run 03-create-lstmf.sh first."; exit 1; }
LSTMF_COUNT=$(wc -l < "$LSTMF_DIR/list.txt" | tr -d ' ')
[ "$LSTMF_COUNT" -gt 0 ] || { echo "ERROR: lstmf/list.txt is empty."; exit 1; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 4 — LSTM Fine-tuning"
echo "  Starting from:  output/ori.lstm  (traineddata: $TRAINEDDATA)"
echo "  Training files: $LSTMF_COUNT .lstmf examples"
echo "  Iterations:     $MAX_ITERATIONS"
echo "  Learning rate:  $LEARNING_RATE"
echo ""
echo "  The training loop prints a loss number every 100 steps."
echo "  You want this number to go DOWN over time."
echo "  A good target: below 0.5 (ideally below 0.2)."
echo ""
echo "  You can safely stop with Ctrl+C — progress is saved"
echo "  to output/ori_histv2_checkpoint every 100 iterations."
echo "  Re-run this script to resume from the last checkpoint."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Checkpoint selection — sorts by iteration number (field 4), picks highest = most recent.
# This is correct for continuing training: resume where you left off, not from best BCER.
# (05-package.sh separately handles selecting the best BCER checkpoint for packaging.)
#
# Override: set CONTINUE_FROM=/path/to/specific.checkpoint before running to force a choice.
if [ -z "$CONTINUE_FROM" ]; then
  # Check new prefix first; fall back to old chapakala19_ prefix for continuity
  RECENT_CHECKPOINT=$(ls "$OUTPUT"/ori_histv2_*.checkpoint "$OUTPUT"/chapakala19_*.checkpoint 2>/dev/null | \
    grep -v '_checkpoint$' | sort -t_ -k4 -n | tail -1)
  if [ -n "$RECENT_CHECKPOINT" ]; then
    CONTINUE_FROM="$RECENT_CHECKPOINT"
    echo "→ Continuing from most recent checkpoint: $(basename $CONTINUE_FROM)"
  elif [ -f "$OUTPUT/ori_histv2_checkpoint" ]; then
    CONTINUE_FROM="$OUTPUT/ori_histv2_checkpoint"
    echo "→ Resuming from rolling checkpoint: $CONTINUE_FROM"
  else
    CONTINUE_FROM="$OUTPUT/ori.lstm"
    echo "→ Starting fresh from ori.lstm"
  fi
else
  echo "→ Using explicit checkpoint: $(basename $CONTINUE_FROM)"
fi

echo ""

OLD_TD_ARG=""
if [ -n "$OLD_TRAINEDDATA" ]; then
  OLD_TD_ARG="--old_traineddata $OLD_TRAINEDDATA"
fi

lstmtraining \
  --continue_from      "$CONTINUE_FROM" \
  --model_output       "$OUTPUT/ori_histv2" \
  --traineddata        "$TRAINEDDATA" \
  $OLD_TD_ARG \
  --train_listfile     "$LSTMF_DIR/list.txt" \
  --learning_rate      "$LEARNING_RATE" \
  --net_mode           16 \
  --max_iterations     "$MAX_ITERATIONS" \
  --target_error_rate  -1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Training done at $MAX_ITERATIONS iterations."
echo "  Checkpoint saved to: output/ori_histv2_checkpoint"
echo ""
echo "  NEXT STEP → ./05-package.sh  (creates the .traineddata)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
