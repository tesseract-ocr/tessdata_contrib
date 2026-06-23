# hoc: a Tesseract model for Ho (Warang Citi) documents

`hoc.traineddata` is a fine-tuned Tesseract LSTM model for OCR of Ho language text in the Warang Citi script. It is fine-tuned from the Latin base model, since Warang Citi is an alphabetic script with uppercase and lowercase letters, similar to Latin. There is no publicly available OCR model for Warang Citi — this is the first, released so that community-led improvement, extension, and further training can follow.

The current best model is `hoc.traineddata` inside `best/`, and that file will be updated as training improves. If you are improving `hoc.traineddata` through training, we request you to submit it as a PR here so others can use and build on it.

The model is trained using open-source fonts including **Noto Sans Warang Citi** and **Boyo Gagrai Unicode**, and on open-licensed Ho language text from the [Ho Wikipedia Incubator](https://incubator.wikimedia.org/wiki/Wp/hoc) and [OFDN Ho OER](https://theofdn.org/oer/ho/).

## About Warang Citi

Warang Citi (𑣁𑣂𑣃𑣄) is the script created by **Lako Bodra** for the Ho language, spoken by ~1.5 million people primarily in Jharkhand, Odisha, and West Bengal.

- Unicode block: U+118A0–U+118FF (Supplementary Multilingual Plane)
- 32 capital letters, 32 small letters, 10 digits, 9 number words, Om symbol

## Current accuracy and known limitations

The model recognizes individual Warang Citi characters well on clean printed text, but has significant limitations:

| Test category | Character accuracy (ignoring spaces) |
|---|---|
| Synthetic text (Noto Sans WC) | **97.8%** |
| Synthetic text (GhanshyamBodra) | **86.3%** |
| Flatbed scans (Noto pages) | 42.0% |
| Flatbed scans (BoyoGagrai pages) | 3.1% |

**Known issues:**

- **No space detection** — the model outputs characters without word boundaries. Every line is one unbroken string. Post-processing is needed to insert spaces.
- **Poor scan recognition** — accuracy drops significantly on real scanned documents compared to clean rendered text.
- **Page segmentation fails** — Tesseract's built-in page segmenter cannot reliably detect text lines in Warang Citi. Pre-segmented line images work best (PSM 13).
- **Training BCER vs real-world gap** — the reported 5.99% training BCER was measured on training data, where near-perfect synthetic lines pull the average down. Independent benchmark on scans shows much lower accuracy.

This model is released as a starting point for community improvement, not as a production-ready tool.

## Usage

Install `best/hoc.traineddata` into your Tesseract tessdata directory, then:

```bash
# OCR a pre-segmented line image (best results)
tesseract line.png stdout -l hoc --psm 13 --oem 1 | python3 tools/pua-to-warang.py

# OCR a full page (results will be poor due to segmentation issues)
tesseract page.png stdout -l hoc --psm 3 --oem 1 | python3 tools/pua-to-warang.py
```

**Important:** OCR output must be piped through `tools/pua-to-warang.py` to convert from internal PUA codepoints to real Warang Citi Unicode. See the PUA mapping section below for why.

## How to help improve this model

- **Test on your own Ho documents** and report how it performs — any feedback helps
- **Contribute more corpus text** — any Ho text in Warang Citi Unicode can be used for training
- **Scan more printed Ho documents** and create ground-truth transcriptions
- **Train an improved model** and submit a PR with the updated `hoc.traineddata` in `best/`
- **Verify the GhanshyamBodra ASCII→Unicode mapping** — this font is used in most Ho publishing but its character mapping needs verification by a native reader

## PUA mapping

Tesseract 5.x cannot handle Warang Citi's SMP codepoints (above U+FFFF) in its internal recoder. This project maps them to the BMP Private Use Area:

```
Warang Citi U+118A0-U+118FF → PUA U+E000-U+E05F
```

The model learns identical glyph shapes. OCR output is post-processed via `tools/pua-to-warang.py` to produce real Warang Citi Unicode. The mapping is defined in `pua_mapping.json`.

## Repository layout

```text
hoc/
├── best/
│   └── hoc.traineddata          # Current best model
├── corpus/
│   ├── clean-corpus.py          # Clean mixed-script text
│   ├── render-corpus.py         # Render corpus into training images
│   ├── hoc_clean.txt            # Cleaned corpus (Warang Citi Unicode)
│   └── hoc_clean_pua.txt        # Cleaned corpus (PUA-encoded for training)
├── fonts/
│   ├── NotoSansWarangCiti-Regular.ttf
│   └── WarangCiti-PUA.ttf       # PUA-mapped font for training
├── scripts/
│   ├── 01-prep-base.sh          # Prepare base traineddata
│   ├── 02-make-lstmf.sh         # Generate LSTMF training files
│   ├── 03-train-finetune.sh     # Fine-tune from Latin base
│   ├── 03-train.sh              # From-scratch training
│   ├── 04-package.sh            # Package checkpoint into traineddata
│   ├── 05-test.sh               # Quick OCR test
│   └── 06-scan-to-lstmf.py      # Convert scans into training material
├── tools/
│   ├── pua-to-warang.py         # Convert PUA output → Warang Citi Unicode
│   ├── benchmark.py             # Accuracy benchmarking
│   ├── augment-synthetic.py     # Noise augmentation
│   └── check-plateau.sh         # Training plateau detection
├── test-images/benchmark/       # Scan images + ground truth for testing
├── pua_mapping.json             # Warang Citi ↔ PUA mapping
└── README.md
```

## Training workflow

1. Prepare the base model and training environment
2. Clean and render the corpus into image and ground-truth pairs
3. Generate `.lstmf` training files
4. Fine-tune from Latin base model
5. Package and test the resulting model

## Training data (Run3, current)

| Type | Files | Description |
|------|-------|-------------|
| Flatbed scans (Noto) | 407 lines (15 pages) | Corpus printed in Noto Sans WC, scanned at 300 DPI |
| Flatbed scans (BoyoGagrai) | 300 lines (12 pages) | Corpus printed in BoyoGagrai Unicode, scanned |
| Synthetic — Noto Sans WC | 414 lines | Rendered from corpus |
| Synthetic — GhanshyamBodra | 414 lines | Rendered using phonetic ASCII→PUA mapping |
| Synthetic augmented | 100 lines | Noise, blur, contrast variations |
| **Total** | **1635** | **Scan:Synth = 707:928** |

## Technical details

- **Engine**: Tesseract 5.x LSTM, fine-tuned from Latin base model
- **Network**: Conv+LSTM transferred from Latin, output layer rebuilt for Warang Citi (80 classes)
- **Unicharset**: 80 entries (PUA-mapped Warang Citi + punctuation)
- **Learning rate**: 0.001 (fine-tuning), auto-reduced at stage 1
- **Best training BCER**: 5.99% at iteration 61300

## Attribution

Coordination and model training: Subhashish Panigrahi.

### Text contributors
- **Ganesh Birua** — Ho language text
- **Mangu Purty** — Ho language text and OER content
- **Subhashish Panigrahi** — Ho language text, OER content, and project coordination

### Text sources
- [Ho Wikipedia Incubator](https://incubator.wikimedia.org/wiki/Wp/hoc) — CC BY-SA
- [OFDN Ho OER](https://theofdn.org/oer/ho/) — by Koshi Purty, CC BY-SA 4.0
- [Warang Chiti Blog](https://warangchiti.blogspot.com/) — Ho language content

### Fonts
- **Noto Sans Warang Citi** — Google Fonts (OFL)
- **Boyo Gagrai Unicode** — Warang Citi Unicode font by Ganesh Birua
- **GhanshyamBodra11** (NewRuleGhanshyamBodra.ttf) — ASCII-encoded Warang Citi font widely used in Ho publishing

## Related

- [Santali (Ol Chiki) training](../sat/) — sister project, same approach
- [OpenSpeaks](https://meta.wikimedia.org/wiki/OpenSpeaks) — community network for Indigenous language documentation

## License

Apache 2.0
