## tesseract_old_persian:

The aim of this project is creating an OCR model (convert image to text) to translate Old Persian Cuneiform.

This project is inspired from [eBL project](https://github.com/ElectronicBabylonianLiterature) and is a part of [
Electronic Old Persian Library](https://github.com/Electronic-Old-Persian-Library) organization.

This tesseract pre-trained OCR model converts Old Persian cuneiform to English transcription.

Notebook: https://github.com/Melanee-Melanee/tessdata_contrib/blob/main/Old_Persian/Tesseract_Old_Persian_OCR.ipynb

Please replace ```op.traineddata``` file in this directory: `/usr/share/tesseract-ocr/4.00/tessdata`



## An example: 

The last 12 lines of the great Darius's inscription in Persepolis, [DPd inscription](https://www.livius.org/sources/content/achaemenid-royal-inscriptions/dpd/):

Input:

![darius2](https://github.com/Melanee-Melanee/Old-Persian-Cuneiform-OCR/assets/74653444/fc8f2a4c-b8b4-4b46-97e3-c87d506fd6fd)



Output:

Zittiy ; iaryvuS ; xrSayZiy;

mnc;aurmzia;upstam; rlauv;

hia ; ViZiriS ; rgiriS ; uta;

im am ; i h yaum ; au lm z i a ;

pitTucs;hca;hinaya; hca;

QuSiyala ; hca;iruga;ariy;

imam ;ihyaum;ma; ajMiya; ait;

aim ;yanm;jDiyaMiy;

aitmiy ; iiaTuv

## At the next stage, we can translate that Old Persian transcription to modern languages by [Chat-GPT](https://chatgpt.com/):

Translate to Modern Persian:




این منم داریوش شاهنشاه؛
به لطف اهورامزدا، من این را بنا کردم؛
من این امپراتوری را بنیان نهادم و آن را نیرومند ساختم.
باشد که اهورامزدا من و پادشاهی مرا محافظت کند؛
باشد که برای همیشه پایدار بماند؛
و باشد که از دروغ در امان باشد؛
این است آنچه من انجام دادم؛

این است آنچه من می‌گویم.

Translate to Modern English:

“This is me, Dariush king; By the grace of Ahura Mazda, I have built this; I founded this empire and made it strong. May Ahuramazda protect me and my kingdom; may it last forever; and it would be safe from lies; that is what I did;
That is what I am saying.”

## Article

I wrote an [article](https://www.researchgate.net/publication/382528886_Translating_Old_Persian_cuneiform_by_artificial_intelligence_AI) as a tiny report for what I have done for this project till now.

## Notice

This [project](https://github.com/Melanee-Melanee/Old-Persian-Cuneiform-OCR) is still under developing. For contributing contact me by email: melaneepython@gmail.com 
