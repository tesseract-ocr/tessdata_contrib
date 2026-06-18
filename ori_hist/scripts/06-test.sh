#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 06-test.sh
#
# Usage:
#   ./06-test.sh                          synthetic test (rendered corpus image)
#   ./06-test.sh image.tif                OCR only — prints ori_histv2 output
#   ./06-test.sh image.tif ground.txt     full comparison: ori vs ori_histv2 + CER table
#
# Both ori and ori_histv2 must be installed in the system tessdata
# (run: cp tessdata_best/ori.traineddata /opt/homebrew/share/tessdata/ once).
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODEL_NAME="ori_histv2"
OUTPUT="$SCRIPT_DIR/output"
TEST_DIR="$SCRIPT_DIR/test-images"
CORPUS="$SCRIPT_DIR/corpus/ori.training_text"
FONT_DIR="$SCRIPT_DIR/fonts"

[ -f "$OUTPUT/${MODEL_NAME}.traineddata" ] || {
  echo "ERROR: output/${MODEL_NAME}.traineddata not found. Run 05-package.sh first."
  exit 1
}

# ── CER/WER python helper (used by modes A and C) ──────────────
cer_wer_py() {
python3 - "$1" "$2" "$3" << 'PYEOF'
import sys, os

def cer_detail(hyp, ref):
    ref, hyp = ref.strip(), hyp.strip()
    if not ref: return 0.0, 0, 0, 0, 0
    m, n = len(ref), len(hyp)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = dp[i-1][j-1] if ref[i-1]==hyp[j-1] else 1+min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1])
    i, j = m, n
    S = D = I = 0
    while i > 0 or j > 0:
        if i>0 and j>0 and ref[i-1]==hyp[j-1]: i-=1; j-=1
        elif i>0 and j>0 and dp[i][j]==dp[i-1][j-1]+1: S+=1; i-=1; j-=1
        elif i>0 and dp[i][j]==dp[i-1][j]+1: D+=1; i-=1
        else: I+=1; j-=1
    return dp[m][n]/len(ref)*100, len(ref)-S-D, S, D, I

def wer_detail(hyp, ref):
    rw, hw = ref.strip().split(), hyp.strip().split()
    if not rw: return 0.0, 0
    m, n = len(rw), len(hw)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = dp[i-1][j-1] if rw[i-1]==hw[j-1] else 1+min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1])
    return dp[m][n]/len(rw)*100, sum(1 for a,b in zip(rw,hw) if a==b)

gt_f, ori_f, new_f = sys.argv[1:]
gt   = open(gt_f).read()
ori  = open(ori_f).read() if os.path.exists(ori_f) else ""
ours = open(new_f).read() if os.path.exists(new_f) else ""

rc = len(gt.strip()); rw = len(gt.strip().split())
cer_o, co, so, do_, io = cer_detail(ori,  gt)
cer_n, cn, sn, dn, ins = cer_detail(ours, gt)
wer_o, wxo = wer_detail(ori,  gt)
wer_n, wxn = wer_detail(ours, gt)
dc = cer_o - cer_n; dw = wer_o - wer_n

print(f"  Ground truth: {rc} chars · {rw} words")
print()
print(f"  {'Metric':<26} {'ori (public)':>14} {'ori_histv2':>14}  {'Δ':>8}")
print(f"  {'-'*26} {'-'*14} {'-'*14}  {'-'*8}")
print(f"  {'CER ↓':<26} {cer_o:>13.1f}%  {cer_n:>13.1f}%  {dc:>+.1f} pp")
print(f"  {'WER ↓':<26} {wer_o:>13.1f}%  {wer_n:>13.1f}%  {dw:>+.1f} pp")
print(f"  {'Chars correct':<26} {co:>5}/{rc} ({100*co/rc:.0f}%)  {cn:>5}/{rc} ({100*cn/rc:.0f}%)")
print(f"  {'Words exact':<26} {wxo:>5}/{rw}        {wxn:>5}/{rw}")
print(f"  {'Substitutions':<26} {so:>14}  {sn:>14}")
print(f"  {'Deletions (missed)':<26} {do_:>14}  {dn:>14}")
print(f"  {'Insertions (halluc.)':<26} {io:>14}  {ins:>14}")
PYEOF
}

# ── Mode C: image + ground-truth → full comparison ─────────────
if [ -n "$2" ]; then
  IMAGE="$1"
  GT="$2"
  STEM=$(basename "${IMAGE%.*}")

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Comparing models on: $(basename $IMAGE)"
  echo "  Ground truth:        $(basename $GT)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  tesseract "$IMAGE" "$TEST_DIR/${STEM}_ori_cmp"  -l ori          --psm 6 2>/dev/null
  tesseract "$IMAGE" "$TEST_DIR/${STEM}_our_cmp"  --tessdata-dir "$OUTPUT" -l "$MODEL_NAME" --psm 6 2>/dev/null

  cer_wer_py "$GT" "$TEST_DIR/${STEM}_ori_cmp.txt" "$TEST_DIR/${STEM}_our_cmp.txt"
  echo ""
  echo "  Raw ori_histv2 output saved to: test-images/${STEM}_our_cmp.txt"
  echo "  Raw ori output saved to:         test-images/${STEM}_ori_cmp.txt"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  exit 0
fi

# ── Mode B: image only → ori_histv2 output ────────────────────
if [ -n "$1" ]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Running ori_histv2 on: $1"
  echo "  (pass a second arg for ground truth + CER comparison)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  tesseract "$1" stdout \
    --tessdata-dir "$OUTPUT" \
    -l "$MODEL_NAME" \
    --psm 6
  echo ""
  exit 0
fi

# ── Mode A: synthetic test ──────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 6 — Testing model (synthetic)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "→ Rendering a fresh test image from corpus..."

head -20 "$CORPUS" > "$TEST_DIR/test_input.txt"

text2image \
  --fonts_dir "$FONT_DIR" \
  --font "Chapakala19" \
  --text "$TEST_DIR/test_input.txt" \
  --outputbase "$TEST_DIR/test_render" \
  --ptsize 24 \
  --xsize 3600 \
  --ysize 480 \
  --resolution 300 \
  --max_pages 0 \
  2>/dev/null

echo "→ Running OCR: ori vs ${MODEL_NAME}..."
echo ""

tesseract "$TEST_DIR/test_render.tif" "$TEST_DIR/ori_result" \
  -l ori --psm 6 2>/dev/null || true

tesseract "$TEST_DIR/test_render.tif" "$TEST_DIR/test_result" \
  --tessdata-dir "$OUTPUT" \
  -l "$MODEL_NAME" \
  --psm 6 2>/dev/null

echo "── Ground truth ─────────────────────────────────────────"
cat "$TEST_DIR/test_input.txt"
echo "────────────────────────────────────────────────────────"
echo ""
echo "── Base ori output ──────────────────────────────────────"
cat "$TEST_DIR/ori_result.txt" 2>/dev/null || echo "(no output)"
echo "────────────────────────────────────────────────────────"
echo ""
echo "── ${MODEL_NAME} output ─────────────────────────────────"
cat "$TEST_DIR/test_result.txt"
echo "────────────────────────────────────────────────────────"
echo ""
echo "── Character Error Rate ─────────────────────────────────"
cer_wer_py "$TEST_DIR/test_input.txt" "$TEST_DIR/ori_result.txt" "$TEST_DIR/test_result.txt"
echo "────────────────────────────────────────────────────────"
echo ""
echo "  Open test-images/test_render.tif in Preview to see the image."
echo ""
echo "  To test on a real scan:"
echo "  ./06-test.sh image.tif                   # ori_histv2 only"
echo "  ./06-test.sh image.tif ground-truth.txt  # full comparison + CER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
