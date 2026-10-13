# bak.traineddata: Bashkort / Bashkir

## Model card

| | |
|---|---|
| Language | Bashkort (Башҡорт теле), also written Bashkir |
| Code | `bak` (ISO 639-3) |
| Script | Cyrillic, 42 letters |
| Speakers | ~1.1 million; classified vulnerable by UNESCO |
| Training | Two-stage fine-tune from `kaz` |
| Author | Rashit Abulyaev (<https://github.com/abulyaev>) |
| Home | <https://github.com/abulyaev/bashkort-ocr> |
| License | Apache-2.0 |

## Model files

| | size | notes |
|---|---|---|
| [best/bak.traineddata](best/bak.traineddata) | 3.2 MB | float, fine-tunable |
| [fast/bak.traineddata](fast/bak.traineddata) | 440 KB | integer |

Neither carries word, punctuation or number dawgs, for the reason in
[Why no dictionary](#why-no-dictionary). The langdata they were originally
built from is in [langdata/](langdata/), so a dictionary build can be
reproduced with `combine_lang_model` by anyone who wants one.

No legacy model; this is LSTM only.

## Why Bashkort needs its own model

Nine Bashkort letters are not in Russian: **ә ө ү ң һ ҙ ҫ ҡ ғ**. Five of them
(**ҙ ҫ ҡ ғ ң**) differ from an ordinary Russian letter only by a descender
below the baseline (ҙ/з, ҫ/с, ҡ/к, ғ/г, ң/н).

**ҫ** (U+04AB), the voiceless interdental fricative /θ/, appears in no existing
Tesseract unicharset. Of the eight Turkic languages already in tessdata, none
can produce it. An existing model cannot represent the letter, so it cannot
output it: `rus` scores 0% recall on all nine letters and `kaz` scores 0% on ҫ.

## Accuracy

157 lines transcribed with no model output in front of the transcriber: no
prefilled suggestion, no machine reading of the page. They were cut from parts
of the books no training data came from, and scored through the `tesseract`
CLI rather than `lstmeval`, which cannot see word splitting.

| model | CER | WER | ҫ | ҙ | ҡ | ғ | ң |
|---|---|---|---|---|---|---|---|
| **bak (best)** | **2.32%** | **13.99%** | **17/17** | 98% | 96% | 99% | 100% |
| bak (fast) | 3.16% | 14.38% | 16/17 | 97% | 97% | 98% | 99% |
| kaz | 5.42% | 24.04% | 0/17 | 87% | 87% | 98% | 99% |
| rus | 21.00% | 76.65% | 0/17 | 0% | 0% | 0% | 0% |

ҫ is given as a count: the set holds 17 instances, and a percentage would
overstate the precision.

Per book, for `best`:

| book | lines | CER | WER |
|---|---|---|---|
| drama anthology | 24 | 4.48% | 31.54% |
| literary collection | 23 | 3.22% | 16.67% |
| historical novel | 14 | 3.17% | 12.68% |
| epic poetry | 21 | 2.84% | 18.33% |
| folk tales | 25 | 2.47% | 13.33% |
| prose collection | 25 | 0.89% | 7.78% |
| historical prose | 25 | 0.60% | 3.61% |

Word error is the weak spot and it concentrates in drama: speaker
attributions, stage directions and dash-led dialogue, where the characters come
out right and the word boundaries do not.

A second, deliberately hard set of 420 lines gives 4.27% CER / 13.03% WER.
Those are lines a previous model got wrong, so the figure is a floor rather
than typical text.

## Why no dictionary

The models were built with `combine_lang_model` from a 120,000-entry
frequency-ordered wordlist plus punctuation and number patterns, all taken from
a 34.6M-character corpus. Measuring what those dawgs contributed showed they
made word error worse on every evaluation set:

| evaluation set | with dawgs | without dawgs |
|---|---|---|
| 157 blind lines | 2.43% CER / 14.88% WER | 2.32% / 13.99% |
| 420 hard lines | 4.24% / 14.71% | 4.27% / 13.03% |
| 420 ordinary lines | 0.41% / 2.75% | 0.46% / 2.68% |

Character error barely moves; word error drops every time the dictionary is
removed.

The likely cause is morphology. Bashkort is agglutinative and inflects heavily,
so a fixed wordlist of any practical size cannot cover the inflectional space.
A word form absent from the list gets pulled toward a present one. That breaks
a whole word while changing one or two characters, which is the shape the
measurements show: a large WER effect and almost no CER effect.

The same may hold for other agglutinative languages in tessdata. This is one
language's measurement and I would not read more into it than that, but it is
cheap to check: `combine_tessdata -u`, delete the three dawg files, repack.

## Training procedure

**Base.** `kaz`, selected by measurement rather than linguistic proximity. It
already recognises eight of the nine Bashkort letters at 81–94%, making this an
"add one character to the output layer" problem. An earlier attempt used `tat`
on the assumption that Tatar is the closest relative. Tesseract's `tat` is a
Latin-script model with no Cyrillic, which invalidated that work.

**Stage 1, 65,967 auto-aligned lines.** Many Bashkort PDFs carry a commercial
OCR text layer. `pdftotext -bbox-layout` gives word boxes; grouping them into
lines and cropping the rendered page at the same coordinates yields image and
text pairs at scale. Noisy, so this stage teaches letterforms only.

**Stage 2, 1,718 human-corrected lines.** Fixes word segmentation and the ҙ/ҫ
confusions stage 1 cannot teach, because its own labels contain them.

Full pipeline, scripts and per-book results:
<https://github.com/abulyaev/bashkort-ocr>

### Notes that may help others

- **Train only on corrected lines.** Training on all 3,321 verified lines gave
  a worse model than the 1,603 the transcriber had actually changed. Labels
  accepted verbatim from the model ask the network to keep doing what it
  already does, and at volume they drown the lines that disagree.
- **Rank checkpoints through `tesseract`, not `lstmeval`.** lstmeval scores the
  raw LSTM without the dictionary and cannot see word splitting, which costs
  one character but two words. It twice selected a checkpoint that fragmented
  words while real WER rose by four points.
- **The learning curve goes flat early.** 400 corrected lines gave 4.53% CER,
  1,718 gave 4.24%, and the 1,200-line run scored worse than the 800-line one.
  Past a few hundred corrected lines the remaining error was display type and
  page layout, not data volume.

## Evaluation data

Transcription elsewhere in the project was prefilled with the model's own
reading for speed, which would make any evaluation drawn from it circular. Two
earlier evaluation sets here were compromised that way; one, built from "lines
no model trained on", turned out to be 90% unchanged lines and produced a
meaningless 0.14% CER.

The figures above therefore come from lines transcribed blind, and the tooling
enforces it: autofill refuses to write a suggestion onto those rows, and
training excludes them.

Where the printed source contained an obvious typo, the transcriber wrote the
correct spelling rather than the misprint. The model therefore loses points for
reading a misprint correctly, which makes these figures slightly pessimistic.

## Training data

Excerpts from seven copyrighted Bashkort books, used with the authors'
permission. Line images and transcriptions are published as release assets at
<https://github.com/abulyaev/bashkort-ocr/releases>.
