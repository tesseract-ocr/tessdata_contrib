# heb_rivok: printed Hebrew, with English, digits and niqqud in the same model

`heb_rivok` (version 2.0) is a Tesseract 5 LSTM model for printed Hebrew: modern documents with
English words and numbers, old print, and vowelled text (niqqud). It is Google's tessdata_best
`script/Hebrew` fine-tuned by [Rivok Labs](https://rivoklabs.com) on real old-print lines and
synthetic Hebrew, Hebrew/English and vowelled lines.

- `best/heb_rivok.traineddata` (12.4 MB): the float model. The most accurate, and the one for further
  fine-tuning.
- `fast/heb_rivok.traineddata` (5.7 MB): its integer conversion (`lstmtraining --convert_to_int`),
  for recognition. This is not a separately trained small network.

```bash
tesseract page.png out -l heb_rivok            # no +eng needed: English is in the model
ocrmypdf -l heb_rivok scanned.pdf searchable.pdf
```

For crops that hold a single line, use `--psm 13` rather than `--psm 7`: Tesseract's line
finder discards crops with an underline or with slivers of neighbouring lines.

Source, model card and evaluation scripts:
https://github.com/RivoksLab/tesseract-heb-rivok (also on
[Hugging Face](https://huggingface.co/Rivok/tesseract-heb-rivok); write-up with examples:
https://rivoklabs.com/research/tesseract-hebrew).

SHA-256:

| file | SHA-256 |
|---|---|
| `best/heb_rivok.traineddata` | `673a4193be1f77565942a69480f3c28c7de9633f25f1fa318162f18fa258ba1b` |
| `fast/heb_rivok.traineddata` | `09ef1830f3393c590791abf9c18deca14450c8e5d3b556249d63b0183cf7a426` |

## Results

Character error rate (lower is better) unless marked, Tesseract 5.5.0. The model is compared with the
tessdata_best model it was fine-tuned from, float against float, with our `fast/` file (int8) next to
it. The last column is `heb` from tessdata_fast, the Ubuntu/Debian package: a smaller, separately
trained network (last layer 128 units against 192 in tessdata_best `heb`), not an int8 copy of
tessdata_best.

| test | `script/Hebrew` (tessdata_best, float) | **heb_rivok 2.0 best (float)** | heb_rivok 2.0 fast (int8) | `heb` (tessdata_fast, the Ubuntu/Debian package) |
|---|---:|---:|---:|---:|
| 150 line crops from real Hebrew documents, Hebrew only (`--psm 13`) | 4.0% | **1.2%** | 1.2% | 4.7% |
| 253 line crops from real documents, with numbers | 3.5% | **1.6%** | 1.6% | 4.5% |
| Four old books (1872–1922), 1,087 lines | 7.8% | **2.6%** | 2.7% | 11.3% |
| … the vowelled Selichot 1885: vowel marks read (higher is better) | 56% | **82%** | 82% | 23% |
| [GlotOCR-bench](https://huggingface.co/datasets/cis-lmu/GlotOCR-bench) Hebrew, clean images (`--psm 6`) | 20.7% | **11.0%** | 10.9% | 21.2% |
| GlotOCR-bench Hebrew, "old document" images | 31.8% | **24.5%** | 25.0% | 34.0% |
| [HaZefira](https://github.com/omilab/historical_press) newspaper (1874/1887), 4,013 line crops | 14.3% | **4.8%** | 4.8% | 17.5% |
| HaZefira, 34 pages: words found (word F1, higher is better) | 75.5% | **92.2%** | 92.1% | 67.6% |
| 209 line crops mixing Hebrew and English | 16.4% | **14.4%** | 14.3% | 19.3% |

- **Settings:** `script/Hebrew` and `heb_rivok` include Latin and run alone; `heb` (tessdata_fast) runs
  with `+eng` on pages and mixed lines.
- **Data:** the line crops come from private documents and can't be shared. The four old books are
  public-domain scans (Wikimedia Commons) with their validated Hebrew Wikisource transcriptions; no
  page of them was used in training. GlotOCR-bench and HaZefira are public, and the repository's
  `eval/` scripts rerun those numbers.
- **Niqqud:** shva, qamats, patah, hiriq, holam, segol, dagesh, hataf patah and the shin/sin dots are
  read reliably; tsere and hataf segol most of the time; qamats qatan, qubuts, meteg and hataf qamats
  often not. Holam haser for vav comes out as holam. Cantillation marks are not read.
- **Character set:** also maqaf ־, geresh ׳, gershayim ״, en and em dash, bullet and €.

## Training

- **Fine-tuning only:** `lstmtraining --old_traineddata`, learning rate 1e-4, on a CPU: 1.0 from
  tessdata_best `script/Hebrew` on synthetic lines; 2.0 continued from 1.0. The released file is an
  average of the weights of the last training checkpoints.
- **Real lines (2.0):** about 24,600 printed lines from public-domain Hebrew books of the 19th and
  early 20th century (scans on Wikimedia Commons, Hebrew Wikisource transcriptions, CC BY-SA 4.0).
- **Synthetic lines:** Tesseract's Hebrew training text (langdata_lstm), document-style and
  Hebrew/English lines, and vowelled text (Tanakh, Mishnah, Project Ben-Yehuda, modern text vowelled
  with Dicta's model), in about 165 open fonts, degraded to look scanned, faxed, faded or photographed.
- **Dictionary:** Tesseract's Hebrew word list plus the 150,000 most frequent English words from
  langdata_lstm.

## Notes for maintainers and users

- **Page direction.** `Tesseract::right_to_left()` comes from `UNICHARSET::major_right_to_left()`. A
  Hebrew model that knows the 52 Latin letters, like this one or Google's `script/Hebrew`, counts as
  left-to-right, so multi-column pages are laid out left column first. Since 1.0.1 the
  `lstm-unicharset` has 23 extra Hebrew characters (presentation forms U+FB1D–FB31 and a few rare
  points), so that right-to-left wins the count. The recoder has no code for them, so the model never
  outputs them. tesseract-ocr/tesseract#4629 proposes a parameter that would make this unnecessary.
- **Short mixed lines.** A short line with as many English words as Hebrew ones comes out left to
  right, English first, because of `ResultIterator::CurrentParagraphIsLtr`'s tie rule
  (tesseract-ocr/tesseract#4680). This happens with every Hebrew model; long paragraphs are not
  affected.
- **Not trained for:** Rashi script, handwriting, decorative display fonts.

## Licence

Apache-2.0, as for the tessdata_best models and langdata_lstm text it is built on. Training-data
credits are in the repository's `NOTICE`. Fonts were used only to render training images and are
not distributed.
