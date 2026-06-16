# Smi: a tesseract model for Sámi

This model was developed for OCR on the Sámi printed material in the collection of the National Library of Norway.  

It can be used for OCR on the following Sámi languages:  
- North Sámi
- South Sámi
- Lule Sámi
- Inari Sámi 


## Training
This model has been trained from the [Norwegian tesseract model](https://github.com/tesseract-ocr/tessdata_best/blob/main/nor.traineddata) from tessdata_best  
It has first been trained for 5 epochs on [Sprakbanken/synthetic_sami_ocr_data](https://huggingface.co/datasets/Sprakbanken/synthetic_sami_ocr_data).  
Then, it has been fine-tuned on a dataset consisting of 93 415 lines of Sámi and Norwegian OCR data (a combination of manually annotated and automatically transcribed data).  
We unfortunately cannot share the data as it copyrighted material.  


Read more about the model training and evaluation in the paper "Comparative analysis of optical character recognition for Sámi texts from the National Library of Norway", accepted for NoDaLiDa/Baltic-HLT 2025 ([link to preprint](https://arxiv.org/abs/2501.07300))

