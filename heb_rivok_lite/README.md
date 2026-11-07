# heb_rivok_lite: printed Hebrew, small and fast

`heb_rivok_lite` (version 1.0) is a Tesseract 5 LSTM model for printed Hebrew and digits. It is
Google's tessdata_best `heb` fine-tuned by [Rivok Labs](https://rivoklabs.com) on synthetic
Hebrew text lines. It is the lighter sibling of [`heb_rivok`](../heb_rivok): about three times
faster per line than `heb_rivok`, at the speed of the standard `heb` model. It has no Latin
letters, so add `eng` for documents with English.

- `best/heb_rivok_lite.traineddata` (6.0 MB): the float model, for further fine-tuning.
- `fast/heb_rivok_lite.traineddata` (3.4 MB): its integer conversion (`lstmtraining --convert_to_int`),
  for recognition. This is not a separately trained small network.

```bash
tesseract page.png out -l heb_rivok_lite+eng
ocrmypdf -l heb_rivok_lite+eng scanned.pdf searchable.pdf
```

Source, model card, training recipe and evaluation scripts:
https://github.com/RivoksLab/tesseract-heb-rivok

SHA-256:

| file | SHA-256 |
|---|---|
| `best/heb_rivok_lite.traineddata` | `baceb6c52bf69550ffae52acad9297619a1b7fc8553890caf299798f7348e4cd` |
| `fast/heb_rivok_lite.traineddata` | `a92584816adf5c9ae38afc255e3530477516318c21c2e711fd57b05535239360` |

## Results

Character error rate (lower is better) unless marked; `fast` model, Tesseract 5.5.0.

| test | `heb` (tessdata_fast) | `heb` (tessdata_best, its start) | **heb_rivok_lite** |
|---|---:|---:|---:|
| 403 line crops from real Hebrew documents, Hebrew only (`--psm 13`) | 4.7% | 4.0% | **1.9%** |
| the same, lines with numbers | 4.5% | 4.3% | **1.6%** |
| [GlotOCR-bench](https://huggingface.co/datasets/cis-lmu/GlotOCR-bench) Hebrew, clean images | 21.2% | 24.6% | **20.6%** |
| GlotOCR-bench Hebrew, "old document" images | 34.0% | 33.5% | **32.3%** |
| [HaZefira](https://github.com/omilab/historical_press) newspaper, 4,013 line crops | 17.5% | 17.7% | **14.1%** |
| HaZefira, 34 pages: words found (word F1, higher is better) | 67.6% | 69.7% | **76.6%** |

- **Model:** the same network as stock `heb`.
- **Page direction:** its character set is Hebrew-only, so pages are laid out right to left as usual.

## Training

- **Fine-tuning only:** `lstmtraining --old_traineddata` from tessdata_best `heb`, learning rate 1e-4, 15,000 iterations on 50,000 synthetic line images.
- **Text:** Tesseract's Hebrew training text (langdata_lstm, Apache-2.0), including vowelled lines, plus generated document-style lines (prices, dates, abbreviations, numbers).
- **Rendering:** 50 open fonts, degraded to look scanned.
- **Characters added:** maqaf ־, geresh ׳ and gershayim ״.
- **Full recipe:** in the repository.

## Licence

Apache-2.0, as for the tessdata_best model and langdata_lstm text it is built on.
