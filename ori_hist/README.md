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

---

## Reproducing the training

Everything needed to reproduce `ori_hist` from scratch is included in this
directory: training corpus, pipeline scripts, and evaluation ground truth.

### Prerequisites

- **Tesseract 5.x** with training tools (`tesseract`, `text2image`, `lstmtraining`,
  `combine_tessdata`)
- **Chapakala 19** font — download `Chapakala19Regular.ttf` from
  [github.com/ofdn/Chapakala](https://github.com/ofdn/Chapakala/tree/main/19)
- **Base model** — `ori.traineddata` from
  [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)
- Python 3 (for corpus-building scripts)

### Directory layout

```
ori_hist/
├── best/
│   └── ori_hist.traineddata          ← the packaged model
├── corpus/
│   ├── ori.training_text             ← 5,251-line Odia training corpus
│   ├── build-quality-corpus.py       ← rebuild corpus from Wikipedia dump
│   └── clean-corpus.py               ← corpus cleaning utilities
├── scripts/
│   ├── 00-setup.sh                   ← install tools, download base model
│   ├── 01-generate-images.sh         ← render corpus → TIFF + box files
│   ├── 02-extract-model.sh           ← extract LSTM from ori.traineddata
│   ├── 03-create-lstmf.sh            ← convert images → .lstmf training files
│   ├── 04-train.sh                   ← run LSTM fine-tuning
│   ├── 05-package.sh                 ← package checkpoint → .traineddata
│   └── 06-test.sh                    ← evaluate model against ground truth
├── test-images/
│   ├── 001.png, 002.png, 003.png     ← 1875-era Odia book crops
│   ├── 1875_1.png                    ← 1875 Odia Bible full page
│   ├── Rath1910-1.png                ← 1910 Odia dharma text
│   └── *.gt.txt                      ← manually typed ground truth
└── README.md                         ← this file
```

### Step-by-step

The scripts expect a working directory laid out as follows. Copy the `corpus/`
and `scripts/` contents from this directory, then download the font and base model.

```
workdir/
├── corpus/
│   └── ori.training_text
├── fonts/
│   └── Chapakala19Regular.ttf
├── tessdata_best/
│   └── ori.traineddata
├── 00-setup.sh … 06-test.sh
```

**Step 0 — Setup**

```bash
./00-setup.sh
```

Downloads `ori.traineddata` from tessdata_best and clones tesstrain for reference.

**Step 1 — Generate training images**

```bash
./01-generate-images.sh 5800
```

Renders the first 5,800 corpus lines through Chapakala 19 at 300 DPI using
`text2image` with `--degrade_image true --rotate_image true` to simulate
letterpress ink spread and page tilt. Produces a multi-page TIFF and
ground-truth `.box` file. Output: **9,571 rendered pages**.

**Step 2 — Extract the base LSTM**

```bash
./02-extract-model.sh
```

Extracts `ori.lstm` from the base `ori.traineddata`.

**Step 3 — Create .lstmf training files**

```bash
./03-create-lstmf.sh
```

Converts TIFF + box pairs into `.lstmf` files that `lstmtraining` reads.
The ori_hist model was trained on **10,264 training lines**.

**Step 4 — Train**

```bash
lstmtraining \
  --continue_from  output/ori.lstm \
  --model_output   output/ori_hist \
  --traineddata    tessdata_best/ori.traineddata \
  --train_listfile lstmf/list.txt \
  --max_iterations 100000
```

Training ran for **100,000 iterations** on an Apple M1 Max (single-threaded CPU,
~112 iterations/minute, ~15 hours total). Best BCER: **1.190%** at iteration
98,900.

To prevent machine sleep during long runs:

```bash
caffeinate -i ./04-train.sh    # macOS
```

**Step 5 — Package**

```bash
./05-package.sh
```

Converts the best checkpoint into `ori_hist.traineddata`.

Note (Tesseract 5.5.x, macOS): `lstmtraining --stop_training` prepends a
~196-byte corrupt header to the `.lstm` output. `05-package.sh` strips this
automatically.

**Step 6 — Test**

```bash
./06-test.sh test-images/1875_1.png test-images/1875_1.gt.txt
```

Runs OCR with both `ori` and `ori_hist` and computes CER and WER against
ground truth.

### Training corpus

The corpus (`corpus/ori.training_text`) contains **5,251 lines** combining:

1. **Advisory lines** (~800) — all 3-virama conjuncts with every matra
   combination, kerning/spacing pairs, full character inventory from the
   Chapakala font advisory files.
2. **Odia Wikipedia prose** (~4,400) — cleaned sentences from a full Odia
   Wikipedia dump (June 2025), filtered to ≥ 85% Odia characters, capped at
   80 chars/line, danda-ending sentences prioritised.

Corpus cleaning rules:
- No Hindu-Arabic numerals (0–9); only Odia numerals (୦–୯)
- No punctuation except Odia danda (। ॥)
- No ZWNJ (U+200C) — historical letterpress did not use it
- Lines capped at 80 characters, split at last space
- Minimum 85% Odia characters per line, minimum 5 Odia characters

To rebuild the corpus from a fresh Wikipedia dump:

```bash
python3 corpus/build-quality-corpus.py
```

### Test images and ground truth

Five held-out evaluation images with manually typed transcriptions:

| Image | Source | Era | GT chars | GT words |
|-------|--------|-----|-------:|-------:|
| 001.png | Odia poetry (cropped) | 19th c. | 136 | 27 |
| 002.png | Odia prose (cropped) | 19th c. | 438 | 85 |
| 003.png | Odia prose (cropped) | 19th c. | 1,111 | 205 |
| 1875_1.png | Bible, Matthew ch.1 (full page) | 1875 | 1,769 | 295 |
| Rath1910-1.png | *Achara Shiksha* dharma text | 1910 | 1,166 | 184 |

None of these images were used during training.

### Font

Training uses **[Chapakala 19](https://github.com/ofdn/Chapakala/tree/main/19)**
(OFL-licensed), a revival of a 19th-century Odia letterpress typeface designed by
Subhashish Panigrahi. Download from the
[Chapakala repository](https://github.com/ofdn/Chapakala).

## Licence

Apache 2.0 — same as the base `ori` model this was fine-tuned from.

## Attribution

Trained by **Subhashish Panigrahi** and the **[O Foundation (OFDN)](https://theofdn.org)**.
Fine-tuned from `ori.traineddata` (tessdata_best, © Google, Apache 2.0).
