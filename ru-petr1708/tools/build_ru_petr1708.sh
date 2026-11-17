#!/bin/sh
# Build ru-petr1708.traineddata: the fine-tuned LSTM plus a pre-reform dictionary.
#
# lstmtraining emits a recogniser and nothing else -- LSTM weights, unicharset
# and recoder -- so the model that comes off the fine-tune has no dawgs, and a
# tesseract model carrying no word dawg cannot use its dictionary-based decoding
# path. It falls back on raw character likelihood, which on nineteenth-century
# type is where the avoidable errors come from. This packs the dictionary in.
# Nothing is retrained: the LSTM, unicharset and recoder are copied byte for
# byte out of the model named on the command line.
#
# This is the same operation tools/build_orusd.sh performs for stock orus, and
# the difference between the two is the point of the project. orus has 133
# characters and no code for fita or izhitsa, so filtering the word list against
# its unicharset drops 2130 entries -- precisely the words spelled with the
# letters being added -- and no dictionary can teach a model to produce a
# character it cannot represent. Against this model's 137 characters nothing is
# dropped, so the dawg carries Ѳеодоръ and ѵпостась and can reinforce in
# decoding the four letters the fine-tune taught the recogniser to see.
#
# The punctuation and number lists are read out of rus.traineddata with
# dawg2wordlist and recompiled here rather than copied. A dawg encodes
# characters by their index in the unicharset it was built against, and this
# unicharset is not stock rus's -- it has four entries rus does not. A dawg
# lifted across is not merely wrong, it is wrong silently: it loads, and it
# matches the wrong characters.
#
# Prerequisites: tesseract plus its training tools -- combine_tessdata,
# wordlist2dawg, dawg2wordlist. On Homebrew these come with `brew install
# tesseract`; on Debian they are in `tesseract-ocr` and `libtesseract-dev`.
# Check with `wordlist2dawg -h` before starting.
#
#     sh tools/build_ru_petr1708.sh work/models/ru-petr1708.r10.traineddata \
#         ru-petr1708-hunspell-3.1/ru_petr1708/ru_petr1708.dic [rus.traineddata]
#
# Writes ./ru-petr1708.traineddata. Install by copying it wherever
# `tesseract --list-langs` looks, then use it as `-l ru-petr1708`. It sits
# beside orusd rather than replacing it; both remain selectable.
set -eu

MODEL=${1:?usage: build_ru_petr1708.sh MODEL.traineddata WORDLIST.dic [RUS.traineddata]}
DIC=${2:?usage: build_ru_petr1708.sh MODEL.traineddata WORDLIST.dic [RUS.traineddata]}
HERE=$(cd "$(dirname "$0")" && pwd)
STOCK=$(tesseract --list-langs 2>&1 | sed -n '1s/.*"\(.*\)".*/\1/p')
RUS=${3:-$STOCK/rus.traineddata}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "=== 1. unpack the fine-tuned model (note the absence of any dawg) ==="
combine_tessdata -u "$MODEL" "$WORK/ru-petr1708." >/dev/null
ls "$WORK" | sed 's/^/    /'

echo
echo "=== 2. filter the word list to what this unicharset can represent ==="
# Expected to drop nothing. If this reports unrepresentable characters, the
# model handed in is not the fine-tuned one -- check that it has 137 entries.
python3 "$HERE/filter_wordlist.py" "$DIC" \
        "$WORK/ru-petr1708.lstm-unicharset" "$WORK/words.txt"

echo
echo "=== 3. lift the punctuation and number patterns out of stock rus ==="
combine_tessdata -u "$RUS" "$WORK/rus." >/dev/null
dawg2wordlist "$WORK/rus.lstm-unicharset" "$WORK/rus.lstm-punc-dawg" \
              "$WORK/punc.txt" >/dev/null
dawg2wordlist "$WORK/rus.lstm-unicharset" "$WORK/rus.lstm-number-dawg" \
              "$WORK/num.txt" >/dev/null
echo "    punc patterns: $(wc -l < "$WORK/punc.txt")"
echo "    number patterns: $(wc -l < "$WORK/num.txt")"

echo
echo "=== 4. compile the three dawgs against this model's unicharset ==="
# The names matter. Tesseract loads a dawg by its exact suffix, so a file named
# anything else is simply not loaded and the build appears to succeed while
# changing nothing.
for pair in "words.txt:ru-petr1708.lstm-word-dawg" \
            "punc.txt:ru-petr1708.lstm-punc-dawg" \
            "num.txt:ru-petr1708.lstm-number-dawg"; do
    src=${pair%%:*}; dst=${pair#*:}
    wordlist2dawg "$WORK/$src" "$WORK/$dst" \
        "$WORK/ru-petr1708.lstm-unicharset" >/dev/null 2>&1
    echo "    $dst  $(wc -c < "$WORK/$dst") bytes"
done

echo
echo "=== 5. repack ==="
rm -f "$WORK"/rus.*
combine_tessdata "$WORK/ru-petr1708." >/dev/null
cp "$WORK/ru-petr1708.traineddata" ./ru-petr1708.traineddata
echo "    wrote $(pwd)/ru-petr1708.traineddata"
combine_tessdata -d ./ru-petr1708.traineddata 2>&1 | grep -E 'dawg|unicharset|lstm:'
