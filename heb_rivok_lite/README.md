# heb_rivok_lite: printed Hebrew with niqqud, at the standard model's speed

`heb_rivok_lite` (version 2.0) is a Tesseract 5 LSTM model for printed Hebrew and digits, including
old print and vowelled text (niqqud). It is Google's tessdata_best `heb` fine-tuned by
[Rivok Labs](https://rivoklabs.com) on real old-print lines and synthetic Hebrew and vowelled lines.
It is the lighter sibling of [`heb_rivok`](../heb_rivok) and runs at the speed of the standard `heb`
model. It has no Latin letters, so add `eng` for documents with English.

- `best/heb_rivok_lite.traineddata` (6.1 MB): the float model, for further fine-tuning.
- `fast/heb_rivok_lite.traineddata` (3.5 MB): its integer conversion (`lstmtraining --convert_to_int`),
  for recognition. This is not a separately trained small network.

```bash
tesseract page.png out -l heb_rivok_lite+eng
ocrmypdf -l heb_rivok_lite+eng scanned.pdf searchable.pdf
```

Source, model card and evaluation scripts:
https://github.com/RivoksLab/tesseract-heb-rivok

SHA-256:

| file | SHA-256 |
|---|---|
| `best/heb_rivok_lite.traineddata` | `3e70e4bdaac955add0cf25f4666ece244795cf7d523f4a4d3dfe52fa1b8b13d5` |
| `fast/heb_rivok_lite.traineddata` | `59da073ad0bca9449fa5a965996e49d0e2bee3c17e8b0b4e2769d67a7ce34c40` |

## Results

Character error rate (lower is better) unless marked; `fast` model, Tesseract 5.5.0.

| test | `heb` (tessdata_fast) | `heb` (tessdata_best, its start) | heb_rivok_lite 1.0 | **heb_rivok_lite 2.0** |
|---|---:|---:|---:|---:|
| 150 line crops from real Hebrew documents, Hebrew only (`--psm 13`) | 4.7% | 4.0% | 1.9% | **1.7%** |
| 253 line crops, with numbers | 4.5% | 4.3% | 1.6% | **1.5%** |
| Four old books (1872–1922), 1,087 lines | 11.3% | 11.2% | 11.4% | **4.8%** |
| … the vowelled Selichot 1885: vowel marks read (higher is better) | 23% | 17% | 18% | **61%** |
| [GlotOCR-bench](https://huggingface.co/datasets/cis-lmu/GlotOCR-bench) Hebrew, clean images | 21.2% | 24.6% | 20.6% | **13.2%** |
| GlotOCR-bench Hebrew, "old document" images | 34.0% | 33.5% | 32.3% | **27.8%** |
| [HaZefira](https://github.com/omilab/historical_press) newspaper, 4,013 line crops | 17.5% | 17.7% | 14.1% | **6.3%** |
| HaZefira, 34 pages: words found (word F1, higher is better) | 67.6% | 69.7% | 76.6% | **91.0%** |

- **Model:** the same network as stock `heb`, so the same speed.
- **Page direction:** its character set is Hebrew-only, so pages are laid out right to left as usual.
- **Niqqud:** 2.0 adds tsere, holam, hataf vowels, qubuts, qamats qatan, meteg, rafe and the shin/sin
  dots to the shva, hiriq, segol, patah, qamats and dagesh that 1.0 read. On heavily vowelled text
  `heb_rivok` is more accurate.

## Training

- **Fine-tuning only:** `lstmtraining --old_traineddata`, learning rate 1e-4: 1.0 from tessdata_best
  `heb` on synthetic lines; 2.0 continued from 1.0 with real old-print lines (public-domain books,
  Hebrew Wikisource transcriptions) and synthetic Hebrew and vowelled lines. The released file is an
  average of the weights of the last training checkpoints.
- **Characters added:** maqaf ־, geresh ׳, gershayim ״ (1.0); the niqqud above and em dash (2.0).

## Licence

Apache-2.0, as for the tessdata_best model and langdata_lstm text it is built on. Training-data
credits are in the repository's `NOTICE`.
