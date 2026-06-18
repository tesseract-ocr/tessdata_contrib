# ori_hist: a Tesseract model for historical Odia letterpress documents

`ori_hist` is a fine-tuned Tesseract 5 LSTM model for OCR of Odia text printed in
19th- and early 20th-century letterpress typefaces. It was developed by
[Subhashish Panigrahi](https://github.com/psubhashish) and the
[O Foundation (OFDN)](https://theofdn.org) as part of a project to make historical
Odia documents -- newspapers, magazine, early science literature, government records and even religious texts -- machine-readable.

The existing `ori` model (last updated 2017) was trained on modern digital Odia fonts
with clean, uniform strokes. It fails on letterpress material because letterpress
fonts have ink spread at stroke intersections, slightly irregular baselines, and
historically distinct letterform shapes, especially in conjuncts and matras. This was the basis of building the [Chapakala](https://github.com/ofdn/Chapakala) typeface revival project. The first set of training was done with [Chapakala 19](https://github.com/ofdn/Chapakala/tree/main/19), an open source typeface designed by Panigrahi between 2024 and 2026.

## Training

`ori_hist` starts from `ori` (tessdata_best) and was fine-tuned on a corpus of
**5,800 lines** combining:

1. Advisory glyph-coverage tables — all 3-virama conjuncts with every matra
   combination, kerning and spacing pairs, full character inventory. These lines
   appear first to guarantee coverage of rare clusters.
2. Odia Wikipedia prose — 4,800 lines of real sentences, cleaned to ≥ 85% Odia
   characters, capped at 80 chars/line, danda-ending sentences prioritised.

Training images were rendered with `text2image` using **Chapakala 19** — a revival
of a 19th-century Odia letterpress typeface designed by Subhashish Panigrahi —
at 300 DPI with `--degrade_image true --rotate_image true` to simulate ink spread
and page tilt found in real documents. The `.lstmf` file contains **10,264 training
lines** (9,571 rendered pages).

**Training command:**

```shell
lstmtraining \
  --continue_from  output/ori.lstm \
  --model_output   output/chapakala19 \
  --traineddata    tessdata_best/ori.traineddata \
  --train_listfile lstmf/list-combined.txt \
  --max_iterations 100000
```

Training ran for **100,000 iterations** on an Apple M1 Max (single-threaded CPU,
~112 iterations/minute, ~15 hours total). Best BCER: **1.190%** at iteration 98,900.

The full training pipeline, corpus-building scripts, and reproducibility notes are
available at:
[github.com/ofdn/tessdata_contrib](https://github.com/ofdn/tessdata_contrib)

## Results

Tested on three image sets against manually typed ground truth.

**1875 Odia Bible scan** — real letterpress photograph, 1,771 chars, 295 words

| Model | CER ↓ | WER ↓ | Chars correct |
|-------|-------|-------|---------------|
| ori (public tessdata_best) | 48.1% | 88.8% | 72% |
| **ori_hist** | **17.2%** | **55.9%** | **87%** |

**Chapakala 19 rendered text** — synthetic letterpress-style image, 1,312 chars, 189 words

| Model | CER ↓ | WER ↓ | Chars correct |
|-------|-------|-------|---------------|
| ori (public tessdata_best) | 38.7% | 87.3% | 72% |
| **ori_hist** | **11.4%** | **31.7%** | **92%** |

**Noto Sans Oriya rendered text** — modern digital font unseen during training,
1,312 chars, 189 words. Included to verify no regression on contemporary documents.

| Model | CER ↓ | WER ↓ | Chars correct |
|-------|-------|-------|---------------|
| ori (public tessdata_best) | 12.8% | 40.7% | 91% |
| **ori_hist** | 13.9% | 43.9% | 89% |

The −1.1 pp regression on Noto Sans reflects Wikipedia footnote markers
(`[୧]`, `[୨]`) and hyperlink text in the test image, not a degradation in
general Odia knowledge. The fine-tuned model reads historical letterpress
**27–31 percentage points more accurately** than the public baseline with
negligible impact on modern fonts.

## Usage

```bash
# Install
cp ori_hist.traineddata /usr/share/tesseract-ocr/4.00/tessdata/   # Linux
cp ori_hist.traineddata /opt/homebrew/share/tessdata/              # macOS Homebrew

# Run
tesseract document-scan.tif output -l ori_hist

# Compare against the base model
tesseract document-scan.tif out_base  -l ori
tesseract document-scan.tif out_hist  -l ori_hist
```

Use `ori_hist` for:
- Pre-independence Odia printed material (newspapers, religious texts, government records)
- Documents using 19th–early 20th century Odia letterpress typefaces
- Any Odia scan where `ori` produces excessive substitutions and hallucinated characters

Use `ori` for modern digital Odia text, contemporary scans, and any document
printed after ~1960.

## Licence

Apache 2.0 — same as the base `ori` model this was fine-tuned from.

## Attribution

Trained by **Subhashish Panigrahi** and the **[O Foundation (OFDN)](https://theofdn.org)**.
Fine-tuned from `ori.traineddata` (tessdata_best, © Google, Apache 2.0).
