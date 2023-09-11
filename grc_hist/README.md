# grc_hist: a tesseract model for historical documents written in (polytonic) greek

`grc_hist` was developed in the context of the project [AjaxMultiCommentary](https://github.com/AjaxMultiCommentary/). It is our best Tesseract model for recognition of historical documents written in (polytonic) greek. 

**Training.** This model starts from `grc`, updates its dictionary and was fine-tuned with 35K+ of real-life ground-truth lines for 40 epochs. This model is the best checkpoint on our evaluation data and was produced at epoch 23. 

Fine-tuning datasets are [GT-commentaries-OCR](https://github.com/AjaxMultiCommentary/GT-commentaries-OCR) and  [Pogetra](https://zenodo.org/record/4774201), which contain a very broad set of images in terms of period, font, type and style. 

The training command used is the following (to be used once training requirements are fixed):

```shell
cd /your/tesstrain/dir
export TESSDATA_PREFIX=/your/tessdata_best/dir
export LD_LIBRARY_PATH=/your/lib/dir # ~/anaconda3/lib depending on your installation 
	make training MODEL_NAME=grc_hist START_MODEL=grc GROUND_TRUTH_DIR=/your/path/to/dir/containing/both/datasets/
LANGDATA_DIR=/your/lib/langdata_lstm/dir/ TESSDATA=/your/tessdata_best/dir/ DATA_DIR=/your/dir/ CORES=30 EPOCHS=40 LEARNING_RATE=0.0001 PSM=7 RATIO_TRAIN=0.95 TARGET_ERROR_RATE=0.001
```

**Results**. Tested on both datasets and on altered images, `grc_hist` drastically surpasses `grc` with performance getting up to .007% on greek characters. The table below shows the results of our main experiments with error rates for characters, words and greek characters only.


| model    | test_dataset | chars_ER | words_ER | greek_chars_ER |
| -------- | ------------ | -------- | -------- | -------------- |
| grc      | ajmc         | .096     | .347     | .091           |
| grc      | pogretra     | .059     | .214     | .049           |
| grc_hist | ajmc         | .013     | .061     | .011           |
| grc_hist | pogretra     | .015     | .05      | .007           |



**Usage**. The model could be of great value for libraries, researchers and anyone interested in historical greek documents. 
