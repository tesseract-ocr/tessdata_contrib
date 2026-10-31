# sat: a Tesseract model for Santali (Ol Chiki) documents

`sat.traineddata` is a Tesseract LSTM model for Santali text in the Ol Chiki script. It is the first LSTM model for Ol Chiki.

## Training

The model is fine-tuned from `Latin.traineddata` (tessdata_best). Ol Chiki is an alphabet, so Latin is a closer starting point than an abugida such as Odia.

Training used a 1:1 mix of synthetic and scanned lines:

- 108 synthetic lines, rendered in Noto Sans Ol Chiki (Regular, Bold) and Guru Gomke (Regular, Italic).
- 107 scanned lines from four pages of *ᱜᱟᱱᱟᱝ ᱟᱨ ᱪᱤᱴᱷᱤ ᱥᱟᱠᱟᱢ (Gānāṁ ār ciṭhi sākām)* (2008) by Hajam Baskey. The ground truth was transcribed by hand.

Final training BCER was 0.78% at sub-iteration 66,800.

The corpus, scripts and test images are in the training repository: https://github.com/ofdn/tesseract-training-santali

## Results

Character accuracy on four scanned pages of *Gānāṁ ār ciṭhi sākām*, with spaces removed from both sides (PSM 6, OEM 1). The legacy `sat` model from [Indic OCR](https://github.com/indic-ocr/tessdata) by RKVS Raman is shown for reference.

| Page | sat (this model) | Indic OCR (OEM 0) |
|------|------------------|-------------------|
| 1 | 74.9% | 81.2% |
| 13 | 62.7% | 74.2% |
| 17 | 58.9% | 71.4% |
| 23 | 62.6% | 76.7% |

Known limitations:

- The model does not output spaces between words.
- This is an early model. More scanned pages with ground truth will improve it.

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
