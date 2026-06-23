# Ho (Warang Citi) Tesseract OCR Training

Training an LSTM OCR model for the **Ho language** in **Warang Citi** script using Tesseract 5.x.

## About Warang Citi

Warang Citi (𑣁𑣂𑣃𑣄) is the script created by **Lako Bodra** for the Ho language, spoken by ~1.5 million people primarily in Jharkhand, Odisha, and West Bengal. The script has uppercase and lowercase letters (like Latin), its own digits, and number words for tens.

- Unicode block: U+118A0–U+118FF (Supplementary Multilingual Plane)
- 32 capital letters, 32 small letters, 10 digits, 9 number words, Om symbol

## Quick start

```bash
# 1. Prepare base model
./01-prep-base.sh

# 2. Render synthetic training data
python3 render-corpus.py

# 3. Convert to training files
./02-make-lstmf.sh

# 4. Process scanned pages
python3 06-scan-to-lstmf.py <image.png> <gt.txt> --prefix <name>

# 5. Train
caffeinate -i ./03-train.sh > logs/training.log 2>&1 &

# 6. Package
./04-package.sh

# 7. Test (output needs PUA→Warang Citi conversion)
tesseract scan.png stdout -l hoc_v1 --psm 6 --oem 1 | python3 tools/pua-to-warang.py
```

## PUA mapping

Tesseract 5.x cannot handle Warang Citi's SMP codepoints (above U+FFFF) in its internal recoder. This project maps them to the BMP Private Use Area:

```
Warang Citi U+118A0-U+118FF → PUA U+E000-U+E05F
```

The model learns identical glyph shapes. OCR output is post-processed via `tools/pua-to-warang.py` to produce real Warang Citi Unicode. The mapping is defined in `pua_mapping.json`.

## Training data (Run3, current)

| Type | Files | Description |
|------|-------|-------------|
| Flatbed scans (Noto) | 407 lines (15 pages) | Original corpus printed in Noto, scanned at 300 DPI |
| Flatbed scans (BoyoGagrai) | 300 lines (12 pages) | New corpus printed in BoyoGagrai Unicode, scanned |
| Synthetic - Noto Sans WC | 414 lines | Rendered from corpus |
| Synthetic - GhanshyamBodra | 414 lines | Rendered using phonetic ASCII→PUA mapping |
| Synthetic augmented | 100 lines | Noise, blur, contrast variations |
| **Total** | **1635** | **Scan:Synth = 707:928** |

## Project structure

```
hoc-tesseract-training/
├── 01-prep-base.sh          # Create base traineddata
├── 02-make-lstmf.sh         # PNG+GT → lstmf
├── 03-train.sh              # From-scratch LSTM training
├── 04-package.sh            # Checkpoint → traineddata
├── 05-test.sh               # Quick OCR test
├── 06-scan-to-lstmf.py      # Scan page → line training data
├── corpus/                  # Source text, PDF, per-page GT
├── fonts/                   # Warang Citi fonts (original + PUA-mapped)
├── rendered/                # Synthetic line images
├── lstmf/                   # Training files (rendered, scan, augmented)
├── output/                  # Unicharset, checkpoints, models
├── tessdata_best/           # Base traineddata + script files
├── test-images/benchmark/   # Scan images + GT for testing
├── tools/                   # Augmentation, plateau check, PUA conversion
├── logs/                    # Training logs
├── pua_mapping.json         # Warang Citi ↔ PUA mapping
├── SESSION_HANDOFF.md       # Private technical handoff
└── README.md                # This file
```

## Current best model (Run3)

- **Training BCER**: 5.99% — **94% character accuracy**
- **Training data**: 1635 files (707 scan + 828 synthetic + 100 augmented)
- **Font styles**: Noto Sans Warang Citi + GhanshyamBodra (phonetic PUA mapping)
- **Scan sources**: 15 Noto pages + 12 BoyoGagrai pages (flatbed, 300 DPI)
- **Model file**: `output/hoc_run3_best.traineddata`

## Technical details

- **Engine**: Tesseract 5.x LSTM, fine-tuned from Latin base model
- **Network**: Conv+LSTM transferred from Latin, output layer rebuilt for Warang Citi (80 classes)
- **Unicharset**: 80 entries (PUA-mapped Warang Citi + punctuation)
- **Learning rate**: 0.001 (fine-tuning), auto-reduced at stage 1
- **PUA workaround**: Warang Citi SMP codepoints mapped to BMP Private Use Area for Tesseract compatibility

## Training text sources and attribution

### Text contributors
- **Ganesh Birua** — Ho language text
- **Mangu Purty** — Ho language text and OER content
- **Subhashish Panigrahi** — Ho language text, OER content, and project coordination

### Text sources
- [Ho Wikipedia Incubator](https://incubator.wikimedia.org/wiki/Wp/hoc) — Wikipedia articles in Ho/Warang Citi (CC BY-SA)
- [OFDN Ho OER](https://theofdn.org/oer/ho/) — Open educational resources for Ho language, by Koshi Purty (CC BY-SA 4.0)
- [Warang Chiti Blog](https://warangchiti.blogspot.com/) — Ho language content

### Fonts
- **Noto Sans Warang Citi** — Google Fonts (OFL)
- **GhanshyamBodra11** (NewRuleGhanshyamBodra.ttf) — ASCII-encoded Warang Citi font widely used in Ho publishing. Requires ASCII→Unicode conversion mapping for use with Unicode training data.

## Related

- [Santali (Ol Chiki) training](../sat-tesseract-training/) — sister project, same approach
- [OpenSpeaks](https://meta.wikimedia.org/wiki/OpenSpeaks/Tools) — community network for Indigenous language documentation
