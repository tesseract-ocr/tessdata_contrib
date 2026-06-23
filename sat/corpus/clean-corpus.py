#!/usr/bin/env python3
"""
clean-corpus.py

Reads text1.txt, strips non-Santali characters, and writes a clean
Ol Chiki corpus suitable for text2image / Pillow rendering.

Keeps:
  - Ol Chiki block U+1C50–U+1C7F (all 48 code points)
  - Common punctuation used in Santali text: . , : ? ! - / " ' ( ) *
  - ASCII digits 0–9 (page numbers, section markers)
  - ASCII space

Removes:
  - Latin letters A–Z / a–z (English words mixed into corpus)
  - Devanagari and other script chars
  - Control characters

Lines with fewer than 5 Ol Chiki characters after cleaning are dropped.
Lines longer than MAX_CHARS are split at word boundaries.
"""

import re
import unicodedata
from pathlib import Path

INPUT  = Path("text1.txt")
OUTPUT = Path("corpus/sat_corpus.txt")
MAX_CHARS = 70

OUTPUT.parent.mkdir(exist_ok=True)

KEEP_ASCII = set(' .,;:?!-/"\')(]*%0123456789')

def is_ol_chiki(c):
    return 0x1C50 <= ord(c) <= 0x1C7F

def clean_line(line):
    chars = []
    for c in line:
        if is_ol_chiki(c):
            chars.append(c)
        elif c in KEEP_ASCII:
            chars.append(c)
        # everything else (Latin letters, Devanagari, symbols) → drop
    cleaned = re.sub(r'  +', ' ', ''.join(chars)).strip()
    return cleaned

def ol_chiki_count(s):
    return sum(1 for c in s if is_ol_chiki(c))

def split_at_boundary(line, max_len):
    """Split a long line at word boundaries so each part ≤ max_len."""
    if len(line) <= max_len:
        return [line]
    words = line.split(' ')
    parts = []
    current = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + 1 > max_len and current:
            parts.append(' '.join(current))
            current = [w]
            cur_len = len(w)
        else:
            current.append(w)
            cur_len += len(w) + 1
    if current:
        parts.append(' '.join(current))
    return parts

raw = INPUT.read_text(encoding='utf-8').splitlines()
out_lines = []
dropped = 0

for line in raw:
    cleaned = clean_line(line)
    if ol_chiki_count(cleaned) < 5:
        if cleaned.strip():
            dropped += 1
        continue
    for part in split_at_boundary(cleaned, MAX_CHARS):
        if ol_chiki_count(part) >= 5:
            out_lines.append(part)

OUTPUT.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')

print(f"Input lines:  {len(raw)}")
print(f"Output lines: {len(out_lines)}")
print(f"Dropped (<5 Ol Chiki chars): {dropped}")
print(f"Written to: {OUTPUT}")
