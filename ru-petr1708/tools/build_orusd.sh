#!/bin/sh
# Build orusd.traineddata: the orus LSTM plus a pre-reform dictionary.
#
# orus is a fine-tune of tesseract's Russian for pre-reform orthography, and it
# ships as LSTM weights, unicharset and recoder only -- with no dawgs at all. A
# tesseract model carrying no word dawg cannot use its dictionary-based decoding
# path and falls back on raw character likelihood, which on nineteenth-century
# type is where the avoidable errors come from.
#
# This packs ru_petr1708 into orus as a word dawg, and brings across stock rus's
# punctuation and number patterns. Nothing is retrained: the LSTM, unicharset
# and recoder are copied through byte for byte.
#
# The punctuation and number lists are read out of rus.traineddata with
# dawg2wordlist and recompiled here rather than copied. A dawg encodes
# characters by their index in the unicharset it was built against, so a dawg
# lifted from one model into another is not merely wrong, it is wrong silently:
# it loads, and it matches the wrong characters.
#
# Prerequisites: tesseract plus its training tools -- combine_tessdata,
# wordlist2dawg, dawg2wordlist. On Homebrew these come with `brew install
# tesseract`; on Debian they are in `tesseract-ocr` and `libtesseract-dev`.
# Check with `wordlist2dawg -h` before starting.
#
#     sh tools/build_orusd.sh orus.traineddata \
#         ru-petr1708-hunspell-3.1/ru_petr1708/ru_petr1708.dic [rus.traineddata]
#
# Writes ./orusd.traineddata. Install by copying it wherever
# `tesseract --list-langs` looks, then use it as `-l orusd`.
set -eu

ORUS=${1:?usage: build_orusd.sh ORUS.traineddata WORDLIST.dic [RUS.traineddata]}
DIC=${2:?usage: build_orusd.sh ORUS.traineddata WORDLIST.dic [RUS.traineddata]}
RUS=${3:-$(dirname "$ORUS")/rus.traineddata}
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "=== 1. unpack orus (note the absence of any dawg) ==="
combine_tessdata -u "$ORUS" "$WORK/orusd." >/dev/null
ls "$WORK" | sed 's/^/    /'

echo
echo "=== 2. filter the word list to what this unicharset can represent ==="
# Read the exclusions printed here. They are a limitation of the result: a
# letter the model has no code for cannot be taught by any dictionary.
python3 "$HERE/filter_wordlist.py" "$DIC" \
        "$WORK/orusd.lstm-unicharset" "$WORK/words.txt"

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
echo "=== 4. compile the three dawgs against orus's unicharset ==="
# The names matter. Tesseract loads a dawg by its exact suffix, so a file named
# anything else is simply not loaded and the build appears to succeed while
# changing nothing.
for pair in "words.txt:orusd.lstm-word-dawg" \
            "punc.txt:orusd.lstm-punc-dawg" \
            "num.txt:orusd.lstm-number-dawg"; do
    src=${pair%%:*}; dst=${pair#*:}
    wordlist2dawg "$WORK/$src" "$WORK/$dst" "$WORK/orusd.lstm-unicharset" \
        >/dev/null 2>&1
    echo "    $dst  $(wc -c < "$WORK/$dst") bytes"
done

echo
echo "=== 5. repack ==="
rm -f "$WORK"/rus.*
combine_tessdata "$WORK/orusd." >/dev/null
cp "$WORK/orusd.traineddata" ./orusd.traineddata
echo "    wrote $(pwd)/orusd.traineddata"
combine_tessdata -d ./orusd.traineddata 2>&1 | grep -E 'dawg|unicharset|lstm:'
