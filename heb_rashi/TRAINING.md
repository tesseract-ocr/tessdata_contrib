

# Creating Tesseract training data

The instructions bellow were tested on Linux Debian 11.

```
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev unzip tmux openmpi-bin
mkdir -p ~/tessdata_heb_rashi/langdata/heb
```


## Word list

Generate Torah literature related [word list](tesseract_4.1.1/langdata/heb/heb.wordlist) from [Sefaria's MongoDB dump](https://storage.googleapis.com/sefaria-mongo-backup/dump_small.tar.gz) with words ordered by decreasing frequency.

```
# Download the dump, decompress and import it:

wget https://storage.googleapis.com/sefaria-mongo-backup/dump_small.tar.gz
tar -xzf dump_small.tar.gz
mongorestore dump


# Convert ' (i.e. \x{27}) and \" to geresh/gershayim and replace each non-Hebrew letter group with a newline, etc.:

mongo sefaria --eval "db.getCollection('texts').find({'language': 'he'}).forEach(function(f){print(tojson(f, '', true));})" | perl -Mutf8 -CS -pE 's/\x{27}/׳/g;s/\\"/״/g;s/\P{Hebrew}+/\n/g;s/^״+$//gm' > texts_hebrew_only.txt


# Sort while counting and eliminating duplicates/entries with occurrence less than 16:

sort --buffer-size=1G texts_hebrew_only.txt | uniq -c | sort -gr | awk '{if ($1 > 15)  print $2}' > heb.wordlist
```

Afterwards delete several empty lines at the beginning and the end of the `langdata/heb/heb.wordlist` file manually.


## Fonts

[Rashi fonts](https://drive.google.com/file/d/1Um3yGV7dT_6AEs7DQU_oC5GpHwZlzR9N/view?usp=sharing) used to render synthetic training data images are listed inside the [tesseract_4.1.1/langdata/heb/okfonts.txt](tesseract_4.1.1/langdata/heb/okfonts.txt). All fonts from `FontsRashi/Working` worked well for the training:

```
text2image --list_available_fonts --fonts_dir FontsRashi/Working
  0: BenOr Rashi
  1: Guttman Rashi
  2: Guttman Rashi Bold
  3: Mekorot-Rashi Bold
  4: Mekorot-Rashi Medium
  5: Mekorot-Rashi Medium Italic
  6: PFT_Rashi
  7: PFT_Rashi Light
  8: RashiAmiti
  9: Rashy
 10: ZWXLDX+RasheeMF-Medium Medium
```


If you have an idea how to fix the fonts from `FontsRashi/NonWorking` (maybe using [FontForge](https://fontforge.org/) or similar) - please [report](https://gitlab.com/pninim.org/tessdata_heb_rashi/-/issues)!



## Determine xheights for Rashi fonts

File [tesseract_4.1.1/langdata/Hebrew.xheights](tesseract_4.1.1/langdata/Hebrew.xheights) was enhanced by Rashi fonts using `grctraining` as follows:

```
git clone https://ancientgreekocr.org/grctraining.git
cd grctraining
make tools/xheight
cd tools/
./xheight 'Mekorot-Rashi Medium'
... and so on for all fonts listed in okfonts.txt
```


## Download remaining necessary files

```
cd ~/tessdata_heb_rashi/langdata

wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/Hebrew.unicharset
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/Latin.unicharset
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/Latin.xheights
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/radical-stroke.txt
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/font_properties

cd heb

wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/desired_characters
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/forbidden_characters
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/heb.numbers
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/heb.punc
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/heb.singles_text
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/heb.unicharambigs
wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/heb/heb.unicharset
```


## ScrollView

**Optional step:** download and build ScrollView to visualize the training process. Not needed if `lstmtraining --debug_interval -1` (shows text information on every iteration) or `lstmtraining --debug_interval 0` (shows text information on every 100 iterations) are used.

```
# Create ScrollView (optional)

apt install openjdk-11-jdk
git clone https://github.com/tesseract-ocr/tesseract
cd tesseract
./autogen.sh
./configure
cd java
make ScrollView.jar

Now run `lstmtraining` from here to utilize ScrollView.jar
```

## Generate training corpus

```
cd /usr/share/tesseract-ocr
sudo rm language-specific.sh tesstrain.sh tesstrain_utils.sh
sudo wget https://raw.githubusercontent.com/tesseract-ocr/tesseract/4.0/src/training/language-specific.sh
sudo wget https://raw.githubusercontent.com/tesseract-ocr/tesseract/4.0/src/training/tesstrain.sh
sudo wget https://raw.githubusercontent.com/tesseract-ocr/tesseract/4.0/src/training/tesstrain_utils.sh
sudo chmod a+x *sh
```



### Create training data

Use all but one font:

```
mkdir -p ~/tessdata_heb_rashi/output/train
/usr/share/tesseract-ocr/tesstrain.sh --fonts_dir FontsRashi/Working --lang heb --linedata_only --noextract_font_properties --langdata_dir ./langdata  --tessdata_dir /usr/share/tesseract-ocr/4.00/tessdata/ --output_dir output/train --fontlist 'BenOr Rashi' 'Guttman Rashi Bold' 'Mekorot-Rashi Bold' 'Mekorot-Rashi Medium' 'Mekorot-Rashi Medium Italic' 'PFT_Rashi' 'PFT_Rashi Light' 'RashiAmiti' 'Rashy' 'ZWXLDX+RasheeMF-Medium Medium'
```

Since the above command may take a lot of time - it is recommended to run it inside [tmux](https://github.com/tmux/tmux). Furthermore it might be beneficial to run the command for each font separately in a separate `tmux` session, e.g.: `/usr/share/tesseract-ocr/tesstrain.sh --fonts_dir FontsRashi/Working --lang heb --linedata_only --noextract_font_properties --langdata_dir ./langdata  --tessdata_dir /usr/share/tesseract-ocr/4.00/tessdata/ --output_dir output/train --fontlist 'BenOr Rashi'` and so on.

### Create evaluation data 

Use the remaining font for evaluation:

```
mkdir -p ~/tessdata_heb_rashi/output/evaluate
/usr/share/tesseract-ocr/tesstrain.sh --fonts_dir FontsRashi/Working --lang heb --linedata_only --noextract_font_properties --langdata_dir ./langdata  --tessdata_dir /usr/share/tesseract-ocr/4.00/tessdata/ --output_dir output/evaluate --fontlist 'Guttman Rashi'
```

### Train

check the number at the top of `output/train/heb/heb.unicharset` - 72 and use it in the command line bellow (O1c72):

```
OMP_THREAD_LIMIT=11 lstmtraining --debug_interval 0 \
  --traineddata ~/tessdata_heb_rashi/output/train/heb/heb.traineddata \
  --net_spec '[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx256 O1c72]' \
  --model_output ~/tessdata_heb_rashi/output/base --learning_rate 20e-4 \
  --train_listfile ~/tessdata_heb_rashi/output/train/heb.training_files.txt \
  --eval_listfile ~/tessdata_heb_rashi/output/evaluate/heb.training_files.txt \
  --max_iterations 50000 &>~/tessdata_heb_rashi/output/basetrain.log
```


# Test results
```
lstmeval --model ~/tessdata_heb_rashi/output/base_checkpoint \
  --traineddata ~/tessdata_heb_rashi/output/train/heb/heb.traineddata \
  --eval_listfile ~/tessdata_heb_rashi/output/evaluate/heb.training_files.txt
```

# Convert checkpoint to best (float) traindata
```
lstmtraining --stop_training --continue_from output/base_checkpoint --traineddata ~/tessdata_heb_rashi/output/train/heb/heb.traineddata --model_output ~/tessdata_heb_rashi/output/heb_rashi.traineddata
```

# Convert checkpoint to fast (integer) traindata
```
lstmtraining --stop_training --convert_to_int --continue_from output/base_checkpoint --traineddata ~/tessdata_heb_rashi/output/train/heb/heb.traineddata --model_output ~/tessdata_heb_rashi/output/heb_rashi.fast.traineddata
```

