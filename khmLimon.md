# khmLimon.traineddata

* Language - Khmer
* Langcode - khmLimon
* Type of training - Finetune using new fonts
* Contributed by - [@phyrumsk](https://github.com/phyrumsk)

## Training Procedure 

[@phyrumsk](https://github.com/phyrumsk) from [Open Institute Cambodia](https://github.com/OpenInstituteCambodia) finetuned the [tesseract_best engine](https://github.com/OpenInstituteCambodia/tessdata_best) with 6 new Limon fonts such as Limon S1, S2, F1, F2, R1, R2 using the same tesseract netspec.

The accuracy reports show that there is over 10% improvement in the recognition on newly finetuned fonts without any appreciable loss in accuracy for the earlier list.

They used isri-ocr-evaluation-tools to test for accuracy and 2 types of images were tested, images which were generated using text2image command (without noise) and the scan images (with noise).

[Sample of testing images are also included](https://github.com/tesseract-ocr/tessdata_best/files/2066786/2018_06_04_KhmLimon_result_for_github.zip).

## Accuracy Reports

### Accuracy_Tesseract_4.0


Testing   Text: |   | Characters : | 19618 |   |   | Clusters : |   | 11272
-- | -- | -- | -- | -- | -- | -- | -- | --

| No.       | Font Name                | Size | Character Accuracy |          | Cluster Accuracy |          |
|-----------|--------------------------|------|--------------------|----------|------------------|----------|
|           |                          |      | Errors             | Accuracy | Errors           | Accuracy |
| 1         | Khmer OS                 | 12   | 1495               | 92,38%   | 650              | 94,23%   |
| 2         | Khmer OS Battambang      |      | 562                | 97,14%   | 140              | 98,76%   |
| 3         | Khmer OS Bokor           |      | 3288               | 83,24%   | 1846             | 83,62%   |
| 4         | Khmer OS Content         |      | 644                | 96,72%   | 159              | 98,59%   |
| 5         | Khmer OS Fasthand        |      | 4605               | 76,53%   | 2012             | 82,15%   |
| 6         | Khmer OS Freehand        |      | 2184               | 88,87%   | 505              | 95,52%   |
| 7         | Khmer OS Metal Chrieng   |      | 3230               | 83,54%   | 1694             | 84,97%   |
| 8         | Khmer OS Muol            |      | 525                | 97,32%   | 135              | 98,80%   |
| 9         | Khmer OS Muol Light      |      | 3430               | 82,52%   | 2115             | 81,24%   |
| 10        | Khmer OS Muol Pali       |      | 6697               | 65,86%   | 3688             | 67,28%   |
| 11        | Khmer OS Siemreap        |      | 1318               | 93,28%   | 582              | 94,84%   |
| 12        | Khmer OS System          |      | 2338               | 88,08%   | 1076             | 90,45%   |
| 13        | Noto Serif Khmer Bold    |      | 2006               | 89,77%   | 1038             | 90,79%   |
| 14        | Noto Serif Khmer Regular |      | 2043               | 89,59%   | 1045             | 90,73%   |
| Average : |                          |      | 2,454,64           | 87,49%   | 1,191,79         | 89,43%   |

| No.       | Font Name | Size | Character Accuracy |          | Cluster Accuracy |          |
|-----------|-----------|------|--------------------|----------|------------------|----------|
|           |           |      | Errors             | Accuracy | Errors           | Accuracy |
| 1         | Limon F1  | 22   | 11459              | 41,59%   | 7340             | 34,88%   |
| 2         | Limon F2  |      | 11152              | 43,15%   | 7652             | 32,11%   |
| 3         | Limon F3  |      | 8454               | 56,91%   | 5590             | 50,41%   |
| 4         | Limon F4  |      | 17082              | 12,93%   | 10319            | 8,45%    |
| 5         | Limon F5  |      | 12259              | 37,51%   | 7689             | 31,79%   |
| 6         | Limon F6  |      | 6146               | 68,67%   | 3858             | 65,77%   |
| 7         | Limon F7  |      | 6750               | 65,59%   | 4031             | 64,24%   |
| 8         | Limon F8  |      | 5512               | 71,90%   | 3482             | 69,11%   |
| 9         | Limon R1  |      | 7053               | 64,05%   | 4336             | 61,53%   |
| 10        | Limon R2  |      | 8044               | 59,00%   | 4584             | 59,33%   |
| 11        | Limon R3  |      | 10467              | 46,65%   | 5357             | 52,48%   |
| 12        | Limon R4  |      | 11815              | 39,77%   | 7068             | 37,30%   |
| 13        | Limon R5  |      | 9479               | 51,68%   | 5811             | 48,45%   |
| 14        | Limon S1  |      | 2704               | 86,22%   | 1479             | 86,88%   |
| 15        | Limon S2  |      | 2277               | 88,39%   | 1248             | 88,93%   |
| 16        | Limon S3  |      | 2863               | 85,41%   | 1413             | 87,46%   |
| 17        | Limon S4  |      | 4631               | 76,39%   | 3074             | 72,73%   |
| 18        | Limon S5  |      | 2552               | 86,99%   | 1488             | 86,80%   |
| 19        | Limon S6  |      | 4577               | 76,67%   | 2700             | 76,05%   |
| 20        | Limon S7  |      | 2773               | 85,87%   | 1485             | 86,83%   |
| Average : |           |      | 7,402,45           | 62,27%   | 4,500,20         | 60,08%   |

### Acc_LimonS1S2F1F2R1R2Unicode

Engine: Fine Tune For Limon S1, S2, F1, F2, R1 & R2 Unicode

Net_spec value “[1,48,0,1 Ct3,3,16 Mp3,3 Lfys64 Lfx96 Lrx96 Lfx384 O1c1]”

| No.       | Font Name                | Size | Character Accuracy |          | Cluster Accuracy |          |
|-----------|--------------------------|------|--------------------|----------|------------------|----------|
|           |                          |      | Errors             | Accuracy | Misrecognized    | Accuracy |
| 1         | Khmer OS                 | 12   | 1818               | 90,73%   | 900              | 92,02%   |
| 2         | Khmer OS Battambang      |      | 1058               | 94,61%   | 476              | 95,78%   |
| 3         | Khmer OS Bokor           |      | 2746               | 86,00%   | 1599             | 85,81%   |
| 4         | Khmer OS Content         |      | 844                | 95,70%   | 353              | 96,87%   |
| 5         | Khmer OS Fasthand        |      | 5063               | 74,19%   | 2296             | 79,63%   |
| 6         | Khmer OS Freehand        |      | 2370               | 87,92%   | 674              | 94,02%   |
| 7         | Khmer OS Metal Chrieng   |      | 3428               | 82,53%   | 1811             | 83,93%   |
| 8         | Khmer OS Muol            |      | 946                | 95,18%   | 464              | 95,88%   |
| 9         | Khmer OS Muol Light      |      | 1313               | 93,31%   | 720              | 93,61%   |
| 10        | Khmer OS Muol Pali       |      | 6194               | 68,43%   | 3413             | 69,72%   |
| 11        | Khmer OS Siemreap        |      | 1939               | 90,12%   | 1041             | 90,76%   |
| 12        | Khmer OS System          |      | 2562               | 86,94%   | 1248             | 88,93%   |
| 13        | Noto Serif Khmer Bold    |      | 2270               | 88,43%   | 1256             | 88,86%   |
| 14        | Noto Serif Khmer Regular |      | 2334               | 88,10%   | 1278             | 88,66%   |
| Average : |                          |      | 2,491,79           | 87,30%   | 1,252,07         | 88,89%   |


| No.       | Font Name | Size | Character Accuracy |          | Cluster Accuracy |          |
|-----------|-----------|------|--------------------|----------|------------------|----------|
|           |           |      | Errors             | Accuracy | Misrecognized    | Accuracy |
| 1         | Limon F1  | 22   | 2599               | 86,75%   | 1696             | 84,95%   |
| 2         | Limon F2  |      | 3896               | 80,14%   | 2661             | 76,39%   |
| 3         | Limon F3  |      | 4178               | 78,70%   | 2786             | 75,28%   |
| 4         | Limon F4  |      | 14807              | 24,52%   | 9374             | 16,84%   |
| 5         | Limon F5  |      | 4859               | 75,23%   | 3282             | 70,88%   |
| 6         | Limon F6  |      | 2576               | 86,87%   | 1622             | 85,61%   |
| 7         | Limon F7  |      | 4115               | 79,02%   | 2145             | 80,97%   |
| 8         | Limon F8  |      | 3580               | 81,75%   | 2166             | 80,78%   |
| 9         | Limon R1  |      | 2144               | 89,07%   | 1358             | 87,95%   |
| 10        | Limon R2  |      | 3681               | 81,24%   | 1626             | 85,57%   |
| 11        | Limon R3  |      | 8224               | 58,08%   | 3482             | 69,11%   |
| 12        | Limon R4  |      | 9265               | 52,77%   | 4504             | 60,04%   |
| 13        | Limon R5  |      | 3120               | 84,10%   | 1995             | 82,30%   |
| 14        | Limon S1  |      | 1262               | 93,57%   | 612              | 94,57%   |
| 15        | Limon S2  |      | 1557               | 92,06%   | 756              | 93,29%   |
| 16        | Limon S3  |      | 2100               | 89,30%   | 1070             | 90,51%   |
| 17        | Limon S4  |      | 2515               | 87,18%   | 1670             | 85,18%   |
| 18        | Limon S5  |      | 2069               | 89,45%   | 1122             | 90,05%   |
| 19        | Limon S6  |      | 2885               | 85,29%   | 1473             | 86,93%   |
| 20        | Limon S7  |      | 1852               | 90,56%   | 889              | 92,11%   |
| Average : |           |      | 4,064,20           | 79,28%   | 2,314,45         | 79,47%   |
