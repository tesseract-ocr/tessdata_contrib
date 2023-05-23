# akk.traineddata

## Model card

* Language - Akkadian
* Language code - akk
* Type of training - finetuning for LSTM models, training for legacy model
* Contributed by - [@Shreeshrii](https://github.com/Shreeshrii) and [@wincentbalin](https://github.com/wincentbalin)

## Model files

* LSTM model - [akk.traineddata](best/akk.traineddata)
* Fast LSTM model - [akk.traineddata](fast/akk.traineddata)
* Legacy model - [akk.traineddata](legacy/akk.traineddata)

## Training Procedure 

Training was performed by [@Shreeshrii](https://github.com/Shreeshrii) and [@wincentbalin](https://github.com/wincentbalin).

The source data for the LSTM model is provided in the [LSTM langdata](https://github.com/tesseract-ocr/langdata_lstm/tree/main/akk)
repository and for the legacy model in the [legacy langdata](https://github.com/tesseract-ocr/langdata/tree/main/akk) repository.

The description of the training procedure is provided in the [tesstrain wiki](https://github.com/tesseract-ocr/tesstrain/wiki/Akkadian-Cuneiform). The repository with the most recent setup is [here](https://github.com/wincentbalin/tesstrain-akk).

