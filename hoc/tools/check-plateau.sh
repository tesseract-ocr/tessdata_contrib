#!/bin/bash
# Checks if any running lstmtraining has plateaued.
# Plateau = no new best BCER in last 10,000 iterations.
# Outputs JSON for hook consumption or plain text for status line.

PLATEAU_THRESHOLD=10000

# Find any running lstmtraining
PID=$(pgrep lstmtraining 2>/dev/null | head -1)
if [ -z "$PID" ]; then
    echo "no training"
    exit 0
fi

# Find the training log by looking at the lstmtraining command's model_output dir
CMD=$(ps -p "$PID" -o args= 2>/dev/null)
MODEL_OUTPUT=$(echo "$CMD" | grep -o '\-\-model_output [^ ]*' | awk '{print $2}')

if [ -z "$MODEL_OUTPUT" ]; then
    echo "training(no log)"
    exit 0
fi

# Find the most recent log file in the same directory
LOG_DIR=$(dirname "$MODEL_OUTPUT")
LOG_DIR=$(dirname "$LOG_DIR")  # go up from output/ to project root
LOG=$(ls -t "$LOG_DIR"/training*.log 2>/dev/null | head -1)

if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
    echo "training(no log)"
    exit 0
fi

# Get current iteration
CURRENT_ITER=$(tail -20 "$LOG" | grep -o 'iteration [0-9]*/[0-9]*/[0-9]*' | tail -1 | cut -d/ -f3)

# Get last best BCER iteration
LAST_BEST_LINE=$(grep "New best BCER" "$LOG" | tail -1)
BEST_ITER=$(echo "$LAST_BEST_LINE" | grep -o '[0-9]*/[0-9]*/[0-9]*' | cut -d/ -f3)
BEST_BCER=$(echo "$LAST_BEST_LINE" | grep -o 'BCER train=[0-9.]*' | cut -d= -f2)

if [ -z "$CURRENT_ITER" ] || [ -z "$BEST_ITER" ]; then
    echo "training iter:?"
    exit 0
fi

GAP=$((CURRENT_ITER - BEST_ITER))

if [ "$GAP" -gt "$PLATEAU_THRESHOLD" ]; then
    # Output for hook (JSON)
    if [ "$1" = "--json" ]; then
        echo "{\"systemMessage\":\"⚠️ PLATEAU: lstmtraining best BCER ${BEST_BCER}% was ${GAP} iters ago (threshold: ${PLATEAU_THRESHOLD}). Current iter: ${CURRENT_ITER}. Consider stopping.\"}"
    else
        echo "PLATEAU! best=${BEST_BCER}% ${GAP}i ago @${CURRENT_ITER}"
    fi
    exit 2
else
    echo "iter:${CURRENT_ITER} best:${BEST_BCER}% gap:${GAP}"
    exit 0
fi
