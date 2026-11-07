# heb_rivok: printed Hebrew, with English and digits in the same model

`heb_rivok` (version 1.0.1) is a Tesseract 5 LSTM model for printed Hebrew documents that also
contain English words and numbers. It is Google's tessdata_best `script/Hebrew` fine-tuned by
[Rivok Labs](https://rivoklabs.com) on synthetic Hebrew and Hebrew/English text lines.

- `best/heb_rivok.traineddata` (12.3 MB): the float model, for further fine-tuning.
- `fast/heb_rivok.traineddata` (5.7 MB): its integer conversion (`lstmtraining --convert_to_int`),
  for recognition. This is not a separately trained small network.

```bash
tesseract page.png out -l heb_rivok            # no +eng needed: English is in the model
ocrmypdf -l heb_rivok scanned.pdf searchable.pdf
```

For crops that hold a single line, use `--psm 13` rather than `--psm 7`: Tesseract's line
finder discards crops with an underline or with slivers of neighbouring lines.

Source, model card, training recipe and evaluation scripts:
https://github.com/RivoksLab/tesseract-heb-rivok (also on
[Hugging Face](https://huggingface.co/Rivok/tesseract-heb-rivok); write-up with examples:
https://rivoklabs.com/research/tesseract-hebrew).

SHA-256:

| file | SHA-256 |
|---|---|
| `best/heb_rivok.traineddata` | `fcc9c68c83a9a49d555b5e6bdf3232c67878a0def65f77c72cf995ff1ff2c4ce` |
| `fast/heb_rivok.traineddata` | `dd9ba506b4ec6e62119a1334949824137692eada686687e51ac10dbb2f7a3df8` |

## Results

Character error rate (lower is better) unless marked; `fast` model, Tesseract 5.5.0.

| test | `heb` (tessdata_fast, the Ubuntu/Debian package) | **heb_rivok** |
|---|---:|---:|
| 403 line crops from real Hebrew documents, Hebrew only (`--psm 13`) | 4.7% | **1.4%** |
| the same, lines with numbers | 4.5% | **1.6%** |
| [GlotOCR-bench](https://huggingface.co/datasets/cis-lmu/GlotOCR-bench) Hebrew, clean images (`--psm 6`) | 21.2% | **18.5%** |
| GlotOCR-bench Hebrew, "old document" images | 34.0% | **30.1%** |
| [HaZefira](https://github.com/omilab/historical_press) newspaper (1874/1887), 4,013 line crops | 17.5% | **9.9%** |
| HaZefira, 34 pages: words found (word F1, higher is better) | 67.6% | **81.3%** |
| HaZefira, 34 pages: words wrong or out of reading order | 47.9% | **32.3%** |

Against its own starting point, with the same network in full precision (`best` files):

| test | `script/Hebrew` (tessdata_best) | **heb_rivok** (`best`) |
|---|---:|---:|
| 403 real line crops, Hebrew only | 4.0% | **1.4%** |
| the same, lines with numbers | 3.5% | **1.6%** |
| GlotOCR-bench Hebrew, clean / old document | 20.7% / 31.8% | **18.0% / 29.5%** |
| HaZefira, 4,013 line crops | 14.3% | **9.9%** |
| HaZefira, 34 pages, words found | 75.5% | **81.2%** |

- **Data:** the 403 crops come from private documents and can't be shared. GlotOCR-bench and
  HaZefira are public, and the repository's `eval/` scripts rerun those numbers.
- **No overlap:** none of the test images were used in training.
- **Character set:** it also outputs maqaf ־, geresh ׳, gershayim ״, en dash, bullet and €, which
  the stock Hebrew models lack.

## Training

- **Fine-tuning only:** `lstmtraining --old_traineddata` from tessdata_best `script/Hebrew`, learning rate 1e-4, 20,000 iterations on 60,000 synthetic line images, on a CPU.
- **Text:**
  - Tesseract's Hebrew training text ([langdata_lstm](https://github.com/tesseract-ocr/langdata_lstm), Apache-2.0);
  - generated document-style lines: prices with ₪, dates, phone numbers, abbreviations such as ש"ח, prefixed numbers such as ב-2024;
  - Hebrew lines with English inside, and English-only lines.
- **Rendering:** Pillow with raqm, in 50 open fonts, then degraded to look scanned (blur, low resolution, noise, JPEG, specks, binarisation, ink, slight rotation, underlines, neighbouring-line slivers). No real documents were used in training.
- **Dictionary:** Tesseract's Hebrew word list plus the 150,000 most frequent English words from langdata_lstm.
- **Full recipe:** `training/RECIPE.md` in the repository.

## Notes for maintainers and users

- **Page direction (why 1.0.1 exists).** `Tesseract::right_to_left()` comes from
  `UNICHARSET::major_right_to_left()`. A Hebrew model that knows the 52 Latin letters, like this
  one or Google's `script/Hebrew`, counts as left-to-right, so multi-column pages are laid out
  left column first. Version 1.0.1 appends 23 Hebrew characters to the `lstm-unicharset`
  (presentation forms U+FB1D–FB31 and a few rare points), so that right-to-left wins the count.
  - The recoder has no code for them, so the model never outputs them.
  - The network, recoder and dawgs are byte-identical to 1.0, and the recognised text is identical.
  - On the 34 HaZefira pages, words wrong or out of reading order drop from 88.5% to 32.3%.
  - tesseract-ocr/tesseract#4629 proposes a parameter that would make this unnecessary.
- **Short mixed lines.** A short line with as many English words as Hebrew ones comes out left to
  right, English first, because of `ResultIterator::CurrentParagraphIsLtr`'s tie rule
  (tesseract-ocr/tesseract#4680). This happens with every Hebrew model; long paragraphs are not
  affected.
- **Not trained for:** Rashi script, handwriting, cantillation marks. The 12 common niqqud marks
  are read.

## Licence

Apache-2.0, as for the tessdata_best models and langdata_lstm text it is built on. Fonts were
used only to render training images and are not distributed.
