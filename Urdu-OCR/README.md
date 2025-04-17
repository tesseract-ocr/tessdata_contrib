# Urdu OCR - Improved Tesseract Model

This repository provides an enhanced Tesseract OCR model (`urd_naw`) specifically trained for improved text extraction from Urdu script images. This custom model demonstrates significantly better performance compared to the standard Tesseract Urdu model (`urd.traineddata`).

## 📚 Training Dataset

The `urd_naw` model was trained on a comprehensive dataset aggregating Urdu text from diverse sources. This dataset comprises 12,748 image-text pairs, meticulously curated for effective model fine-tuning.

- **Access the dataset:** [Training Dataset Link](https://drive.google.com/file/d/1jbdFo1ea8MxZ7yHOVIcPgP5yOd4ihvBU/view?usp=drive_link)

## 🚀 Training

The model was fine-tuned using the Tesseract training tools. Below is an example command for initiating training on Windows using PowerShell. Please adapt the paths according to your environment setup.

```powershell
# Ensure you are in your tesstrain data directory
cd C:\path\to\your\tesstrain\data

# Set TESSDATA_PREFIX environment variable
$env:TESSDATA_PREFIX = "C:\path\to\your\tessdata_best\data"

# Run the training command
make training MODEL_NAME=urd_naw START_MODEL=urd `
LANGDATA_DIR="C:\path\to\your\langdata_lstm\dir\" `
TESSDATA="C:\path\to\your\tessdata_best\dir\" `
LANG_TYPE=RTL
```

## 📊 Model Performance and Results

The `urd_naw` model exhibits substantial improvements over the baseline `urd` model. Key performance metrics from the training process (Iteration 9724) are summarized below:

| Metric       | Value    | Interpretation                                       |
| :----------- | :------- | :--------------------------------------------------- |
| Mean RMS     | 2.125%   | High accuracy in character shape recognition.        |
| Delta        | 9.981%   | Significant improvement during training iterations.  |
| BCER (train) | 27.125%  | ~73% character-level accuracy on the training set. |
| BWER (train) | 63.071%  | Word-level accuracy, improved but with scope for enhancement. |
| Skip ratio   | 0.100%   | Minimal skipping of image regions during processing. |

**Key Advantages:**

- **Enhanced Recognition:** Superior accuracy for Urdu text compared to the default Tesseract model.
- **Character Accuracy:** More precise recognition at the character level.
- **Complex Script Handling:** Better processing of intricate Urdu script patterns (ligatures, diacritics).
- **Reliability:** Increased robustness for processing real-world Urdu documents.

## 💡 Potential Applications

This improved model is well-suited for various tasks, including:

- Digitizing printed Urdu books and historical documents.
- Extracting text from handwritten Urdu notes or manuscripts.
- Creating searchable text layers for Urdu image archives.
- Assisting researchers and libraries working with Urdu materials.

## 🖼️ Visual Comparison

To visually demonstrate the performance difference, here is a comparison using a sample test image:

**Test Image:**

![Test Urdu Image](DIRECT_LINK_TO_TEST_IMAGE)
*(Original Link: https://drive.google.com/file/d/1V79mvQU8WG92S1ThiM0-yVNE6ZROPWxd/view?usp=drive_link)*

**Model Output Comparison:**

| Model             | Output Image                                       |
| :---------------- | :------------------------------------------------- |
| Standard `urd`    | ![Standard urd model output](DIRECT_LINK_TO_URD_OUTPUT_IMAGE) <br> *(Original Link: https://drive.google.com/file/d/19URq0GefJW800Y9vx6hvq7WnaHQ4tgoU/view?usp=drive_link)* |
| Improved `urd_naw`| ![Improved urd_naw model output](DIRECT_LINK_TO_URD_NAW_OUTPUT_IMAGE) <br> *(Original Link: https://drive.google.com/file/d/1JpIFNyTlDRofG3XB2o8kzPhUzNDzPQM5/view?usp=drive_link)* |

*(Observation: [Optional: Add specific observations about the improvements here, e.g., fewer character errors, better word segmentation in the `urd_naw` output].)*

## 📜 License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.