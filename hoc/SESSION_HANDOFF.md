# Ho (Warang Citi) Tesseract Training — Session Handoff

Private documentation for continuing this work.

## 1. What this project is

Training an OCR model for the **Ho language** written in **Warang Citi** script using Tesseract 5.x LSTM.

**Script properties:** Warang Citi is alphabetic with **uppercase and lowercase** (like Latin). 32 capital letters (U+118A0-U+118BF), 32 small letters (U+118C0-U+118DF), 10 digits, 9 number words (tens 10-90), and the Om symbol. Created by Lako Bodra for the Ho language.

## 2. Critical: PUA mapping workaround

**Tesseract 5.5.2 cannot handle Supplementary Multilingual Plane (SMP) characters** in its recoder. Warang Citi (U+118A0-U+118FF) is in the SMP. We work around this by mapping to the Basic Multilingual Plane's Private Use Area:

```
Warang Citi U+118A0-U+118FF → PUA U+E000-U+E05F
```

- All training data (GT, unicharset, lstmf) uses PUA codepoints
- The model learns identical glyph shapes — PUA maps to the same font glyphs
- OCR output must be post-processed: `tools/pua-to-warang.py`
- Mapping saved in `pua_mapping.json`
- Font with PUA glyphs: `fonts/WarangCiti-PUA.ttf`

**Usage after training:**
```bash
tesseract scan.png stdout -l hoc_v1 --psm 6 --oem 1 | python3 tools/pua-to-warang.py
```

## 3. Training data

### Run1 (current, from-scratch)

| Type | Lines | Source |
|------|-------|--------|
| Scan (7 pages, flatbed) | 189 | Printed from hoc_training_pages.pdf, pages 1-7 |
| Synthetic clean | 150 | Rendered from corpus using WarangCiti-PUA font |
| Synthetic noise-augmented | 40 | Blur, noise, contrast variation |
| **Total** | **379** | **Ratio scan:synth = 1:1** |

Pages 8-15 of the PDF are ready for printing/scanning to add in a future run.

### Scan page details

| Page | Det. lines | GT lines | Notes |
|------|-----------|----------|-------|
| p1 | 27 | 27 | 1 GT line removed (bottom undetected) |
| p2 | 28 | 28 | 1 extra detection auto-trimmed |
| p3 | 28 | 28 | Perfect match |
| p4 | 26 | 26 | 2 GT lines removed |
| p5 | 24 | 24 | 4 GT lines removed (bottom of scan cut off) |
| p6 | 28 | 28 | Bottom artifact filtered |
| p7 | 28 | 28 | Bottom artifact filtered |

Deskew applied to all pages (most tilted 2-2.8°).

## 4. Network architecture

From-scratch training (no base model to fine-tune from):
```
[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx192 O1c82]
```
- 82 output classes: 81 chars in unicharset + 1 CTC blank
- Learning rate: 0.002
- Max iterations: 400,000

## 5. Unicharset

81 entries (extracted by `unicharset_extractor` from PUA corpus):
- 64 Warang Citi letters (as PUA U+E000-E03F, labeled "Latin" for Tesseract compatibility)
- Digits, punctuation, special entries (NULL, Joined, Broken)

File: `output/hoc_pua.unicharset`

## 6. Important: radical-stroke.txt

The `combine_lang_model` tool REQUIRES a valid `radical-stroke.txt` in the script_dir. Without it, recoder creation fails with "Error writing recoder". Downloaded from `tesseract-ocr/langdata_lstm` GitHub repo. Also needed: `Latin.unicharset`, `Common.unicharset` from the same repo.

## 7. Files reference

| File | Description |
|------|-------------|
| `tessdata_best/hoc_base.traineddata` | Base model with PUA unicharset + recoder |
| `corpus/hoc_training_pages.pdf` | 15-page PDF for printing (uses mixed font rendering) |
| `corpus/p1.gt.txt` - `p15.gt.txt` | Per-page GT in PUA encoding |
| `corpus/hoc_clean.txt` | Cleaned corpus (414 lines, original Warang Citi) |
| `corpus/hoc_clean_pua.txt` | Cleaned corpus in PUA encoding |
| `fonts/WarangCiti-PUA.ttf` | Font with PUA codepoint mappings |
| `fonts/NotoSansWarangCiti-Regular.ttf` | Original Warang Citi font |
| `pua_mapping.json` | Warang Citi ↔ PUA bidirectional mapping |
| `tools/pua-to-warang.py` | Post-processing: PUA output → Warang Citi |
| `tools/augment-synthetic.py` | Noise augmentation for synthetic data |
| `tools/check-plateau.sh` | Plateau detection (10K iter stall) |
| `lstmf/list.txt` | Current training list (379 files, 1:1 ratio) |

## 8. Run1 result — PLATEAUED (2026-06-22)

**Run1 plateaued at BCER 98.8% — the model barely learned.**

| Metric | Value |
|--------|-------|
| Best BCER | 98.798% at iter 5000 |
| Plateau detected | iter 16000 (11K stall) |
| Training data | 379 files (189 scan + 190 synthetic) |
| Learning rate | 0.01 (increased from 0.002 which showed zero learning) |
| Model file | `output/hoc_run1_best.traineddata` |

**What happened:** The model briefly touched 98.8% BCER at iter 5000 (barely above random chance for 80 output classes) then bounced back to 100% and never improved again. Even with LR=0.01 (5× the initial 0.002), from-scratch training couldn't converge with only 379 training files and 80 output classes — that's less than 5 examples per character.

**Comparison with Santali:** Santali from-scratch with ~481 files and 75 classes plateaued at 42.5% accuracy. But Santali used Ol Chiki (BMP) directly — here the PUA mapping adds a layer of indirection that may affect training. Also, Warang Citi has case (64 letters vs Ol Chiki's 30) making the task harder per sample.

**Key learning:** From-scratch training needs substantially more data for Warang Citi than we have. The Santali project succeeded by fine-tuning from Latin base model. For Ho, we should either:
1. Collect much more training data (1000+ lines from diverse sources)
2. Try fine-tuning from Latin base model (despite Warang Citi's different visual style, the conv layers may still transfer useful features)
3. Use all 514 synthetic files (drop 1:1 ratio) to give the model more examples

## 9. Run2 — Fine-tuning from Latin (completed, 2026-06-22)

Fine-tuning from Latin base model with 703 files (189 scan + 514 synthetic). LR=0.001.

**Result:**
- Best BCER: **17.94%** at iter 52000 (~82% char accuracy, ~78% word accuracy)
- BWER: 21.6%
- Model: `output/hoc_run2_best.traineddata`
- Test benchmark at BCER 19.4%: 13.6% scan, 7.5% synthetic, 12.2% overall
- Killed to start Run3 with larger dataset

## 9a. Run3 — Fine-tuning from Latin with expanded data (started 2026-06-22)

Fresh fine-tune from Latin base with **1635 files** — 2.3× Run2's dataset.

| Type | Source | Files |
|------|--------|-------|
| Scan - Noto pages 1-15 | Flatbed scans of Noto PDF | 407 |
| Scan - BoyoGagrai m2 pages 1-12 | Flatbed scans of BoyoGagrai PDF | 300 |
| Synth - Noto Sans WC | Rendered from corpus | 414 |
| Synth - GhanshyamBodra | Rendered from corpus (phonetic PUA mapping) | 414 |
| Synth - noise augmented | Blur, noise, contrast variation | 100 |
| **Total** | | **1635** |

Scan:synth ratio = 707:928 ≈ 1:1.3

**Result (plateaued 2026-06-22):**
- Best BCER: **5.99%** at iter 61300 (~94% char accuracy, ~55% word accuracy)
- BWER: 45.0%
- Plateaued after 10K iterations without improvement (iter 71300)
- ~43 epochs (each line seen ~43 times)
- Transitioned to stage 1 (auto LR reduction) at iter 48400
- Model: `output/hoc_run3_best.traineddata`

**Run progression:**
| Run | BCER | Char accuracy | Data | Notes |
|-----|------|---------------|------|-------|
| Run1 (scratch) | 98.80% | 1.2% | 379 | Failed — insufficient for from-scratch |
| Run2 (Latin) | 17.94% | 82.1% | 703 | First successful model |
| **Run3 (Latin)** | **5.99%** | **94.0%** | **1635** | Current best — 2 font styles, BoyoGagrai scans |

## 10. Corpus sources

| Source | File | Warang Citi chars | Notes |
|--------|------|-------------------|-------|
| Original text (blog, wiki) | `corpus/messy.txt` | 12,550 | First corpus, cleaned to 414 lines |
| Wikipedia Incubator + OFDN OER | `corpus/MessyText2.txt` | 15,922 | 57 wiki pages + OFDN content |
| **Total available** | | **~28,500** | Needs cleaning for next training run |

## 11. Ghanshyam Bodra font

`NewRuleGhanshyamBodra.ttf` — ASCII-encoded font used for majority of Ho book publishing.
- Located: `/Users/psubhashish/Documents/Text-Typography/Font/Other scripts/Warang Citi/`
- Copied to: `fonts/` (not yet)
- Maps ASCII A-Z/a-z to Warang Citi glyphs visually
- **No Unicode Warang Citi codepoints** — purely visual encoding
- Specimen sheet: `fonts/ghanshyam_bodra_specimen.png`
- ASCII→Unicode mapping: **preliminary, needs verification by Ho reader**
- PUA F006-F031: combining marks/diacritics — may indicate characters used in practice but not in Unicode standard

**Action needed:** Verify ASCII→Warang Citi mapping, create converter, generate PUA-mapped version for training.

## 12. Attribution

### Text contributors
- **Ganesh Birua** — Ho language text
- **Mangu Purty** — Ho language text and OER content
- **Subhashish Panigrahi** — Ho language text, OER content, and project coordination

### Text sources
- [Ho Wikipedia Incubator](https://incubator.wikimedia.org/wiki/Wp/hoc) — CC BY-SA
- [OFDN Ho OER](https://theofdn.org/oer/ho/) — by Koshi Purty, CC BY-SA 4.0
- [Warang Chiti Blog](https://warangchiti.blogspot.com/)

### Fonts
- Noto Sans Warang Citi — Google Fonts (OFL)
- GhanshyamBodra11 — ASCII-encoded Warang Citi font (widely used in Ho publishing)

## 13. Next steps

1. **Continue Run2** — training still improving at 18.5% BCER
2. **Clean MessyText2.txt** (15,922 WC chars) — nearly doubles available corpus for next run
3. **Verify Ghanshyam Bodra mapping** — create ASCII→Unicode converter, generate PUA font for training
4. Print and scan pages 8-15 for more scan training data
5. When Run2 plateaus, start Run3 with: expanded corpus, both fonts, more scans
