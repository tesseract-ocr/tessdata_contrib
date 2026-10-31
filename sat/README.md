# sat: a Tesseract model for Santali (Ol Chiki) documents

`sat.traineddata` is a Tesseract LSTM model for Santali text in the Ol Chiki script. It is the first LSTM model for Ol Chiki.

## Training

The model is fine-tuned from `Latin.traineddata` (tessdata_best). Ol Chiki is an alphabet, so Latin is a closer starting point than an abugida such as Odia.

This is Run7. It continued from the Run4 checkpoint and trained on 842 line images:

| Type | Lines |
|------|-------|
| Book scans: 13 pages from 5 publications | 336 |
| The Santali Wikisource article on Pandit Raghunath Murmu, printed and scanned on a flatbed: 6 pages | 166 |
| Synthetic: Noto Sans Ol Chiki (Regular, Bold) and Guru Gomke (Regular, Italic) | 240 |
| Synthetic with blur, noise, contrast changes and slight rotation | 100 |

Six of the book pages are from *ᱜᱟᱱᱟᱝ ᱟᱨ ᱪᱤᱴᱷᱤ ᱥᱟᱠᱟᱢ (Gānāṁ ār ciṭhi sākām)* (2008) by Hajam Baskey. The others are 2 pages each of *Guru Gomke* (2004), *Ajay Gada* (2022) and *Rar Sanes*, and 1 page of *Sahayinon* (2021). The ground truth was transcribed by hand.

Best training BCER was 3.61% at iteration 203,600.

The corpus, scripts and test images are in the training repository: https://github.com/ofdn/tesseract-training-santali

## Results

Character accuracy on the 19 scanned pages, with spaces removed from both sides (PSM 6, OEM 1). The legacy `sat` model from [Indic OCR](https://github.com/indic-ocr/tessdata) by RKVS Raman is shown for reference.

All 19 pages were also used in training, so these figures do not show accuracy on unseen pages. A held-out test set is still needed.

| Pages | sat (this model) | Indic OCR (OEM 0) |
|-------|------------------|-------------------|
| *Gānāṁ ār ciṭhi sākām*, 6 pages | 84.1% to 96.7% | 71.4% to 91.7% |
| *Guru Gomke*, 2 pages | 53.9%, 89.9% | 58.2%, 96.7% |
| *Ajay Gada*, 2 pages | 84.7%, 86.5% | 77.3%, 87.2% |
| *Rar Sanes*, 2 pages | 91.7%, 89.6% | 87.0%, 86.3% |
| *Sahayinon*, 1 page | 94.7% | 94.7% |
| Pandit Raghunath Murmu article, 6 pages | 86.0% to 94.9% | 52.0% to 80.6% |
| Mean of 19 pages | 87.2% | 76.8% |

Known limitations:

- The model does not output spaces between words.
- Indic OCR reads the two *Guru Gomke* pages better.
- The figures above come from training pages. Accuracy on new books will be lower.

## Usage

Copy `best/sat.traineddata` into your tessdata directory. Then run:

```bash
tesseract scan.tif output -l sat --psm 6
```

## Credits

Subhashish Panigrahi trained the model. Ramjit Tudu guided the choice of Santali Wikisource books and shared background on earlier Santali OCR work. Prasanta Hembram tested interim models and advised during training.

Text sources, all CC BY-SA 4.0:

- [Santali Wikisource](https://wikisource.org/wiki/Category:%E1%B1%A5%E1%B1%9F%E1%B1%B1%E1%B1%9B%E1%B1%9F%E1%B1%B2%E1%B1%A4) books
- Chapter 1 of [OpenSpeaks](https://en.wikiversity.org/wiki/OpenSpeaks/sat) by Subhashish Panigrahi, translated into Santali by R Ashwani Banjan Murmu, Fagu Baskey and Joy Sagar Murmu
- Santali Wikisource article on [Pandit Raghunath Murmu](https://w.wiki/D$AN)
- [Community Language Documentation & Archiving Training](https://w.wiki/ReCS), translated by Bodi Baski

Fonts: Noto Sans Ol Chiki (SIL Open Font License) and [Guru Gomke](https://github.com/GuruGomke).

## Licence

Apache 2.0, the same as Tesseract.
