# ori_hist training data and reproduction instructions

This directory contains everything needed to reproduce the `ori_hist` model
from scratch: training corpus, pipeline scripts, and evaluation ground truth.

## Prerequisites

- **Tesseract 5.x** with training tools (`tesseract`, `text2image`, `lstmtraining`,
  `combine_tessdata`)
- **Chapakala 19** font — download `Chapakala19Regular.ttf` from
  [github.com/ofdn/Chapakala](https://github.com/ofdn/Chapakala/tree/main/19)
- **Base model** — `ori.traineddata` from
  [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)
- Python 3 (for corpus-building scripts)
- GNU Make 4.x (macOS ships with 3.81; install via `brew install make` on macOS)

### macOS (Homebrew)

```bash
brew install tesseract
```

### Ubuntu/Debian

```bash
apt install tesseract-ocr libtesseract-dev
```

## Directory layout

```
training/
├── corpus/
│   ├── ori.training_text         ← 5,251-line Odia training corpus
│   ├── build-quality-corpus.py   ← script to rebuild corpus from Wikipedia dump
│   └── clean-corpus.py           ← corpus cleaning utilities
├── scripts/
│   ├── 00-setup.sh               ← install tools, download base model
│   ├── 01-generate-images.sh     ← render corpus → TIFF + box files
│   ├── 02-extract-model.sh       ← extract LSTM from ori.traineddata
│   ├── 03-create-lstmf.sh        ← convert images → .lstmf training files
│   ├── 04-train.sh               ← run LSTM fine-tuning
│   ├── 05-package.sh             ← package checkpoint → .traineddata
│   └── 06-test.sh                ← evaluate model against ground truth
├── test-images/
│   ├── 001.png, 002.png, 003.png ← 1875-era Odia book crops
│   ├── 1875_1.png                ← 1875 Odia Bible full page
│   ├── Rath1910-1.png            ← 1910 Odia dharma text
│   └── *.gt.txt                  ← manually typed ground truth for each image
└── README.md                     ← this file
```

## Step-by-step reproduction

The scripts assume a working directory with this layout:

```
ori-tesseract-training/
├── corpus/
│   └── ori.training_text
├── fonts/
│   └── Chapakala19Regular.ttf
├── tessdata_best/
│   └── ori.traineddata
├── 00-setup.sh … 06-test.sh
```

Copy the `corpus/` and `scripts/` contents from this directory into that layout,
then download the font and base model.

### Step 0 — Setup

```bash
./00-setup.sh
```

Downloads `ori.traineddata` from tessdata_best, clones tesstrain for reference.

### Step 1 — Generate training images

```bash
./01-generate-images.sh 5800
```

Renders the first 5,800 corpus lines through Chapakala 19 at 300 DPI using
`text2image`. Produces a multi-page TIFF and ground-truth `.box` file.

Image degradation is enabled (`--degrade_image true --rotate_image true`) to
simulate letterpress ink spread and page tilt.

### Step 2 — Extract the base LSTM

```bash
./02-extract-model.sh
```

Extracts `ori.lstm` from the base `ori.traineddata`.

### Step 3 — Create .lstmf training files

```bash
./03-create-lstmf.sh
```

Converts TIFF + box pairs into `.lstmf` files that `lstmtraining` reads.
The ori_hist model was trained on **10,264 training lines** from 9,571 rendered
pages.

### Step 4 — Train

```bash
lstmtraining \
  --continue_from  output/ori.lstm \
  --model_output   output/ori_hist \
  --traineddata    tessdata_best/ori.traineddata \
  --train_listfile lstmf/list.txt \
  --max_iterations 100000
```

This is the exact training command used to produce `ori_hist`. Training ran for
**100,000 iterations** (~15 hours on Apple M1 Max, single-threaded CPU at
~112 iterations/minute).

Best BCER: **1.190%** at iteration 98,900.

To prevent machine sleep during long training runs:

```bash
caffeinate -i ./04-train.sh    # macOS
```

### Step 5 — Package

```bash
./05-package.sh
```

Converts the best checkpoint into `ori_hist.traineddata`.

**Note (Tesseract 5.5.x, macOS):** `lstmtraining --stop_training` prepends a
~196-byte corrupt header to the `.lstm` output. `05-package.sh` strips this
automatically by locating the `\x00\x06\x00\x00\x00Series` signature.

### Step 6 — Test

```bash
./06-test.sh test-images/1875_1.png test-images/1875_1.gt.txt
```

Runs OCR with both `ori` and `ori_hist`, computes CER and WER against ground
truth.

## Training corpus

The corpus (`corpus/ori.training_text`) contains **5,251 lines** combining:

1. **Advisory lines** (~800) — all 3-virama conjuncts with every matra
   combination, kerning/spacing pairs, full character inventory from the
   Chapakala font advisory files.
2. **Odia Wikipedia prose** (~4,400) — cleaned sentences from a full Odia
   Wikipedia dump (June 2025), filtered to ≥ 85% Odia characters, capped at
   80 chars/line, danda-ending sentences prioritised.

### Corpus cleaning rules

- No Hindu-Arabic numerals (0–9); only Odia numerals (୦–୯)
- No punctuation except Odia danda (। ॥)
- No ZWNJ (U+200C) — historical letterpress did not use it
- Lines capped at 80 characters, split at last space
- Minimum 85% Odia characters per line, minimum 5 Odia characters

To rebuild the corpus from a fresh Wikipedia dump:

```bash
python3 corpus/build-quality-corpus.py
```

This downloads the Odia Wikipedia dump (~41 MB) and produces `ori.training_text`.

## Test images and ground truth

Five held-out evaluation images with manually typed transcriptions:

| Image | Source | Era | GT chars | GT words |
|-------|--------|-----|-------:|-------:|
| 001.png | Odia poetry (cropped) | 19th c. | 136 | 27 |
| 002.png | Odia prose (cropped) | 19th c. | 438 | 85 |
| 003.png | Odia prose (cropped) | 19th c. | 1,111 | 205 |
| 1875_1.png | Bible, Matthew ch.1 (full page) | 1875 | 1,769 | 295 |
| Rath1910-1.png | *Achara Shiksha* dharma text | 1910 | 1,166 | 184 |

None of these images were used during training.

## Font

Training uses **[Chapakala 19](https://github.com/ofdn/Chapakala/tree/main/19)**
(OFL-licensed), a revival of a 19th-century Odia letterpress typeface designed by
Subhashish Panigrahi. The font is not bundled here; download it from the
[Chapakala repository](https://github.com/ofdn/Chapakala).

## Licence

Training corpus and scripts: Apache 2.0.
Ground-truth transcriptions: Apache 2.0.
Test images: scans of public-domain 19th/early 20th century documents.
