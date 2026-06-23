# sat: a Tesseract model for Santali Ol Chiki documents

`sat.traineddata` is a fine-tuned Tesseract model for OCR of Santali text in the Ol Chiki script. It is trained on the Latin base model as Ol Chiki is an alphabetic script, similar to Latin. In the past, community members have tried to train Tesseract but have not yet released it. This model is released publicly so that more community-led improvement, extension, and further training will follow.

This is the first LSTM-based model for Ol Chiki.

The repository is structured so that the current best-trained data file, corpus preparation utilities, training scripts, and test materials are all helpful for reproducing the output. The current base checkpoint is `sat.traineddata` inside `sat/best/`, and that file will be updated as training improves. If you are improving `sat.traineddata` through training, we request you to submit it as a PR here so others can use and build on that.

The model is trained using open-source fonts including **Noto Sans Ol Chiki** and [**Guru Gomke**](https://github.com/GuruGomke). These fonts are also used in corpus rendering for training data generation.

## Repository layout

```text
sat/
├── best/
│   └── ori_hist.traineddata
├── corpus/
│   ├── clean-corpus.py
│   ├── render-corpus.py
│   ├── sat_corpus.txt
│   └── sat_corpus2_clean.txt
├── scripts/
│   ├── 01-prep-base.sh
│   ├── 02-make-lstmf.sh
│   ├── 03-train.sh
│   ├── 04-package.sh
│   ├── 05-test.sh
│   └── 06-scan-to-lstmf.py
└── test-images/
```
