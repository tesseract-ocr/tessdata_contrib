# eng_scans: English for scanned documents, forms and receipts

`eng_scans` is Google's tessdata_best `eng` with its LSTM fine-tuned on document-style lines: prices, dates, phone and
invoice numbers, form labels and running text in serif, sans, typewriter and dot-matrix faces, damaged the way scans
and photos are (blur, noise, JPEG, fading, uneven lighting, bitonal thresholding, printer dots, ink bleed, form rules,
neighbouring lines cut off at the edge), plus line crops from real receipt photos. The network, unicharset, recoder
and word lists are unchanged from `eng`, so it is a drop-in replacement: `tesseract image.png out -l eng_scans`.

**Results.** Character error rate on line crops, Tesseract 5.3.4, `--oem 1 --psm 7`, `eng` against `eng_scans`
(best):

| test set | lines | eng | eng_scans |
|---|---:|---:|---:|
| FUNSD forms (scanned office documents; no form data in training) | 400 | 13.3% | 11.3% |
| SROIE receipts (scans; a different receipt collection from the one trained on) | 400 | 12.4% | 8.3% |
| both, case-insensitive | 800 | 12.9% | 9.8% |
| synthetic English lines, 8 rendering conditions | 2,400 | 0.88% | 0.91% |

Read by the same network with tight line crops (each line cropped to its ink and flat-fielded before scaling, as in the
GPU engine linked below), the 800 real lines go from 13.0% to 9.0% and the synthetic ones from 0.38% to 0.27%.

**Training.** Starting from tessdata_best `eng`, 5,000 steps of CTC training, batch 32, Adam at 1e-4 with warm-up and
cosine decay, on one Tesla T4 (about 6 minutes), using a PyTorch copy of Tesseract's network that matches it to 4e-5;
the trained weights are written back into the `.traineddata` file in place, and every other component is Google's.

- 30,000 generated lines: WikiText-103 sentences and fragments (Wikipedia text, CC BY-SA) and generated receipt and
  form strings, rendered in the training machine's system fonts and 18 SIL OFL fonts from google/fonts.
- 7,779 line crops from CORD v2 receipt photos (naver-clova-ix/cord-v2, CC BY 4.0; train and validation splits).

No test line, and no FUNSD or SROIE image, was used in training. `fast/eng_scans.traineddata` is the same model
converted to 8-bit with `combine_tessdata -c`.

**Code and data.** Everything that produced this model, in the tesseract-gpu experiment
(https://github.com/oaustegard/experiments/tree/main/tesseract-gpu):

- training-line generator, CORD extraction, trainer and Kaggle job: https://github.com/oaustegard/experiments/tree/main/tesseract-gpu/run/ft
- the PyTorch copy of Tesseract's network and the in-place `.traineddata` export: https://github.com/oaustegard/experiments/blob/main/tesseract-gpu/tessgpu/tessnet.py
- evaluation script and scores: https://github.com/oaustegard/experiments/blob/main/tesseract-gpu/run/ft/eval_models.py, https://github.com/oaustegard/experiments/blob/main/tesseract-gpu/results/ft_eval.json
- write-up (Finding 13): https://github.com/oaustegard/experiments/blob/main/tesseract-gpu/RESULTS.md
- this folder as submitted: https://github.com/oaustegard/experiments/tree/main/tesseract-gpu/contrib/eng_scans

**Licence.** Apache-2.0, as a modified version of tessdata_best `eng` (Apache-2.0).
