# fas_print — Persian (`fas`) fine-tuned for modern Iranian print

`fas_print` is Tesseract's `tessdata_best/fas` model fine-tuned on 325k
synthetic Persian text lines in 43 fonts and 1,282 real scanned book lines with
corrected transcriptions. It targets machine-printed Persian as found in
Iranian books, documents and PDFs from the 1980s on. On real scans it makes
3–8× fewer character errors than the stock model, outputs the Persian comma
`،` (which the stock model cannot), reads the Latin words that occur in
Persian documents, and no longer mixes Arabic `ي`/`ك` into Persian text.

| | |
|---|---|
| `best/fas_print.traineddata` | float model, 4.9 MB, most accurate |
| `fast/fas_print.traineddata` | integer model, 2.0 MB, ~2× faster, same accuracy on real scans (see below) |

Trained and tested with Tesseract 5.5.3; works with any Tesseract 5.x
(LSTM engine).

## Usage

```sh
tesseract page.png out -l fas_print                 # default (automatic) page segmentation
tesseract page.png out -l fas_print --psm 6         # single-column documents: keeps numbered lists together
tesseract line.png out -l fas_print --psm 7         # one text line
```

- `--psm 6` is the better choice for single-column pages: on the Iranian
  constitution the automatic mode splits the list numbers into their own
  column and doubles the error rate, for the stock model too.
- The traineddata sets `textord_noise_rejrows 0`, because Tesseract's row
  noise filter rejects about 1 in 6 clean Persian text lines as noise
  (tesseract-ocr/tesseract#4582). Nothing to configure.
- **Multi-column pages** (newspapers, two-column articles): see *Known
  limitations*. Until the upstream fix is merged, run `-l fas+fas_print`
  for such pages (the stock model listed first).
- Like every Tesseract RTL model, the text output contains U+200E/U+200F
  marks where the reading direction changes inside a line (around Latin
  words or numbers). Strip them if you do not want them.

## What is different from the stock model

| Problem in stock `fas` | Cause | `fas_print` |
|---|---|---|
| Can never output the Persian comma `،` | `langdata_lstm/fas/forbidden_characters` bans U+0600–U+0615 | outputs it |
| English words become garbage | no Latin letters in the unicharset | reads Latin text (mixed-script lines were oversampled in training) |
| Mixes `ي`/`ی` and `ك`/`ک` | ~30% of the stock training text uses the Arabic forms | one orthography: Persian `ی` `ک`, Persian digits, no bidi controls, NFC |
| Drops whole text lines | row noise filter | `textord_noise_rejrows 0` in the model config |
| Weak on the fonts Iranian documents use | trained on DejaVu, FreeSerif, Tahoma | 43 fonts, including the classic Iranian book and office faces |
| Missing `ٔ ؤ إ % ٪ ? ; = @` and the dialogue dash | absent from training text | present |

## Evaluation

None of the test material was used for training; the two books' test lines
come from pages excluded from training. CER is the character error rate on
canonical text (orthography counts); word recall is the share of ground-truth
words found anywhere on the page, which is meaningful even when the reading
order differs.

| Test set | stock `fas` | `fas_print` best | `fas_print` fast |
|---|---|---|---|
| 190 lines, 1980s phototypeset bold book (300 dpi), CER | 5.38% | **1.14%** | 1.16% |
| … same, ignoring spacing/ZWNJ conventions | 3.35% | **0.38%** | 0.40% |
| 321 lines, 2010s book (200 dpi PDF scan), CER | 4.65% | **1.25%** | 1.21% |
| 36 random lines, two older scanned novels (150 dpi and 112 dpi metal type), CER | 6.51% | **2.59%** | 2.66% |
| 4 pages, Iranian constitution PDF (`--psm 6`), CER / word recall | 1.30% / 95.0% | **0.25% / 99.0%** | 0.22% / 99.1% |
| 1 full page, 1980s book scan, CER | 5.37% | **1.27%** | 1.27% |
| 1 full page, scanned novel, CER | 2.07% | **0.40%** | 0.40% |
| 2,000 synthetic lines in 4 fonts never trained on, CER | 5.11% | **1.79%** | 2.65% |
| 74 machine-printed pages of [PersianML/persian-ocr-benchmark](https://huggingface.co/datasets/PersianML/persian-ocr-benchmark), word recall | 50.7%¹ | **53.0%** | 52.2% |

¹ stock with `-c textord_noise_rejrows=0`; 49.8% without.

The benchmark pages (web images, forms, old newspapers, screenshots, many
below 100 dpi) are dominated by layout and resolution problems that no
recognition model fixes; page CER there is about 47% for every model because
of reading order on multi-column layouts.

Remaining errors on real scans are mostly spacing: a word space read as ZWNJ
or dropped, and ZWNJ read as a space. The model outputs standard orthography
(`می‌کنم`, `کتاب‌ها` with ZWNJ) even where a book sets them with a visible gap.

## Training data

**Synthetic lines (325k)**, rendered with Pango/Cairo (`text2image`-style)
and degraded (resolution down to ~110 dpi, blur, noise, contrast, JPEG,
skew, binarization with stroke-weight changes and pepper noise, kashida
stretching, narrow and wide word spaces, thinned diacritics):

- 120k lines of Persian Wikipedia sentences ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/))
  in 31 open fonts; lines containing Latin words or Persian punctuation
  oversampled; a share of numbers in Latin digits.
- 100k Wikipedia lines in the 12 classic Iranian book and office faces
  (the "B" family, see *Fonts*).
- 40k lines with fiction typesetting conventions: dialogue dashes,
  ellipses, spaces before punctuation, Arabic-Indic digit shapes.
- 30k lines with binarized-scan degradation only.
- 38k lines of the original `langdata_lstm/fas` training text
  ([Apache-2.0](https://github.com/tesseract-ocr/langdata_lstm)) as rehearsal
  data, so the model keeps what the stock model knows.

**Real lines (1,282, each repeated 40×)**, cut from scanned books with
Tesseract's line boxes and transcribed:

- 665 lines from *ما چگونه ما شدیم* (Sadegh Zibakalam), a 200 dpi PDF scan
  of a 2010s print, transcriptions corrected by hand.
- 617 lines from the Persian translation of Oriana Fallaci's *Interview
  with History* (*مصاحبه با تاریخ*, tr. Pirouz Maleki, Amirkabir), 1980s
  phototypesetting in a bold face, scanned at 300 dpi; transcribed from the
  line crops with a vision-language model (Claude) and checked against the
  OCR output wherever the two disagreed.

The books are copyrighted; the line images are not part of this
contribution. 190 and 321 lines from other pages of the same books are the
first two test sets above.

**Dictionary**: word list rebuilt from Persian Wikipedia word frequencies;
punctuation and number patterns cleaned of bidi controls and extended with
`، ؛ ٪ ٫ ٬`.

### Fonts

Used only to render training images; no font is redistributed.

- OFL: Vazirmatn, Estedad, Amiri, Scheherazade New, Mirza, Noto Naskh
  Arabic, Noto Sans Arabic, Parastoo.
- GPL-2 (FarsiWeb): Nazli, Nazli Bold, Titr, Homa.
- Saber Rastikerdar's free fonts (see their repositories): Sahel, Samim,
  Shabnam, Tanha, Gandom, Nahid.
- Bitstream Vera licence: DejaVu Sans.
- The 12 "B" faces that are the de-facto standard of Iranian print (B
  Nazanin, B Lotus, B Mitra, B Zar, B Badr, B Yagut, B Roya, B Compset,
  B Traffic, B Yekan, B Titr, B Koodak). They circulate freely but without
  a clear licence, which is why they appear only as rendering input here.

Held out from training to measure generalization: Parastoo, Estedad, Homa
and B Yas.

## Training

- Start model: `tessdata_best/fas` (4.00.00alpha, synth20170629).
- [tesstrain](https://github.com/tesseract-ocr/tesstrain) with
  `START_MODEL=fas LANG_TYPE=RTL`, learning rate 0.0001, 100,000 iterations,
  tesstrain's 90/10 train/eval split (338,184 / 37,577 line images), final
  checkpoint (training-eval BCER 1.28%).
- The WordStr box writer was patched to keep ZWNJ and not to mirror brackets
  (tesseract-ocr/tesstrain#430); with the stock
  writer a fine-tuned model unlearns ZWNJ and reverses brackets.
- `fast/` is the same checkpoint converted with `lstmtraining --convert_to_int`.
- The whole pipeline (corpus normalization, rendering, real-line cutting and
  correction tool, evaluation) is at https://github.com/givia/tesseract-fas.

## Known limitations

- **Multi-column pages come out in left-to-right column order.** Tesseract
  decides a model's reading direction by counting its characters' bidi
  classes; because this model knows the 52 Latin letters, it counts as
  left-to-right (53 vs 46), and the column finder does not apply its RTL
  handling. On a two-column article from the benchmark this costs 1,233
  character edits against 259 for the stock model; with the direction fixed
  it is 189. Single-column pages are unaffected. Workarounds: `-l fas+fas_print`
  (the stock model, listed first, sets the direction; twice as slow), or
  Tesseract built with tesseract-ocr/tesseract#4629 and
  `-c tessedit_right_to_left=1`.
- Spacing and ZWNJ are the largest remaining error class on real books
  (see *Evaluation*).
- Old metal type (pre-1970s books, ≤120 dpi) is improved but still at
  2–3% CER: word splits at letter gaps, `آ` at low resolution.
- Latin text in serif faces is weaker than in sans faces; Latin glued to
  Persian without a space cannot be ordered correctly by Tesseract.
- The fast variant is as good as the float one on real scans but 0.9 points
  worse on the synthetic unseen-font set.
- Not trained for handwriting, vertical text or Arabic/Urdu/Kurdish text.

## Licence

Apache-2.0, like the tessdata models it derives from.
