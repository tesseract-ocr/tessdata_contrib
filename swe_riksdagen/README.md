# swe_riksdagen

Experimental Swedish domain model for modern Swedish parliamentary documents.
This is a contributed model and does not replace the standard `swe` model.

## Training

The model was fine-tuned from the Tesseract `swe` model with tesstrain. The
training set contains 2,748 geometrically extracted line images from modern
Riksdag documents. The training pipeline preserves boundaries between
separate PDF `<word>` elements; the source documents are not included here.

Training settings:

- learning rate: `0.00001`
- maximum iterations: `1000`
- line segmentation: `PSM 13` for training
- document evaluation: `PSM 3`

## Evaluation

The split is document-separated: no document occurs in more than one split.
Lower is better.

| Model | Validation CER | Validation WER | Test CER | Test WER |
|---|---:|---:|---:|---:|
| `swe` | 0.978% | 1.448% | 0.926% | 1.196% |
| `swe_riksdagen` | 0.916% | 1.065% | **0.903%** | **1.016%** |

The model is a domain-specific experiment rather than a claim of general
Swedish OCR improvement. Training data provenance, manual review status, and
the complete reproducibility package should be reviewed before this model is
accepted upstream.
