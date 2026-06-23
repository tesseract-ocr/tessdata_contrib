#!/usr/bin/env python3
"""Convert Tesseract PUA output back to Warang Citi Unicode.

The OCR model outputs PUA codepoints (U+E000-E05F) because Tesseract 5.x
can't handle SMP characters (U+118A0+) in its recoder. This script maps
them back to real Warang Citi.

Usage:
    tesseract scan.png stdout -l hoc_v1 | python3 tools/pua-to-warang.py
    python3 tools/pua-to-warang.py < ocr_output.txt
"""
import sys

PUA_TO_WARANG = {chr(0xE000 + i): chr(0x118A0 + i) for i in range(96)}

text = sys.stdin.read()
for pua, wc in PUA_TO_WARANG.items():
    text = text.replace(pua, wc)
sys.stdout.write(text)
