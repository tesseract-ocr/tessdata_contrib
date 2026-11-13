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

Character error rate (lower is better) unless marked; `fast` files except the `script/Hebrew`
column (tessdata_best, its starting point), Tesseract 5.5.0.

| test | `heb` (tessdata_fast, the Ubuntu/Debian package) | `script/Hebrew` (tessdata_best) | heb_rivok 1.0.1 | **heb_rivok 2.0** |
|---|---:|---:|---:|---:|
| 150 line crops from real Hebrew documents, Hebrew only (`--psm 13`) | 4.7% | 4.0% | 1.4% | **1.2%** |
| 253 line crops from real documents, with numbers | 4.5% | 3.5% | 1.6% | **1.6%** |
| Four old books (1872–1922), 1,087 lines | 11.3% | 7.8% | 8.1% | **2.7%** |
| … the vowelled Selichot 1885: vowel marks read (higher is better) | 23% | 56% | 50% | **82%** |
| [GlotOCR-bench](https://huggingface.co/datasets/cis-lmu/GlotOCR-bench) Hebrew, clean images (`--psm 6`) | 21.2% | 20.7% | 18.5% | **10.9%** |
| GlotOCR-bench Hebrew, "old document" images | 34.0% | 31.8% | 30.1% | **25.0%** |
| [HaZefira](https://github.com/omilab/historical_press) newspaper (1874/1887), 4,013 line crops | 17.5% | 14.3% | 9.9% | **4.8%** |
| HaZefira, 34 pages: words found (word F1, higher is better) | 67.6% | 75.5% | 81.3% | **92.1%** |

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
