# hoc: a Tesseract model for Ho (Warang Citi) documents

`hoc.traineddata` is a Tesseract LSTM model for Ho text in the Warang Citi script. It is the first public OCR model for Warang Citi.

Warang Citi was created by Lako Bodra for the Ho language. Its Unicode block is U+118A0 to U+118FF.

## Training

The model is fine-tuned from `Latin.traineddata` (tessdata_best). Warang Citi has capital and small letters, as Latin does.

Training used 1,635 line images:

| Type | Lines |
|------|-------|
| Flatbed scans, text printed in Noto Sans Warang Citi | 407 (15 pages) |
| Flatbed scans, text printed in Boyo Gagrai Unicode | 300 (12 pages) |
| Synthetic, Noto Sans Warang Citi | 414 |
| Synthetic, GhanshyamBodra | 414 |
| Synthetic with noise, blur and contrast changes | 100 |

The corpus, fonts, scripts and benchmark images are in the training repository: https://github.com/ofdn/tesseract-training-ho

## Private Use Area mapping

Tesseract 5 cannot train on Warang Citi code points above U+FFFF. The model therefore uses U+E000 to U+E05F in the Private Use Area. Convert its output to Warang Citi Unicode with `pua-to-warang.py` from the training repository.

## Results

Character accuracy, with spaces removed from both sides:

| Test set | Accuracy |
|----------|----------|
| Synthetic lines, Noto Sans Warang Citi | 97.8% |
| Synthetic lines, GhanshyamBodra | 86.3% |
| Flatbed scans, Noto Sans Warang Citi | 42.0% |
| Flatbed scans, Boyo Gagrai Unicode | 3.1% |

Known limitations:

- The model does not output spaces between words.
- Page segmentation is unreliable. Use line images with `--psm 13`.
- Accuracy on real scans is low. This is an early model for the community to improve.

## Usage

Copy `best/hoc.traineddata` into your tessdata directory. Then run:

```bash
tesseract line.png stdout -l hoc --psm 13 --oem 1 | python3 pua-to-warang.py
```

## Credits

Ganesh Birua contributed Ho text. Mangu Purty contributed Ho text and OER content. Subhashish Panigrahi contributed Ho text and OER content, and trained the model.

Text sources:

- [Ho Wikipedia Incubator](https://incubator.wikimedia.org/wiki/Wp/hoc), CC BY-SA
- [OFDN Ho OER](https://theofdn.org/oer/ho/) by Koshi Purty, CC BY-SA 4.0
- [Warang Chiti blog](https://warangchiti.blogspot.com/)

Fonts:

- Noto Sans Warang Citi (SIL Open Font License)
- Boyo Gagrai Unicode by Mangu Purty, a Unicode version of the Boyo Gagrai font by Boyo Gagrai
- GhanshyamBodra11, an ASCII-encoded font used in Ho publishing

## Licence

Apache 2.0, the same as Tesseract.
