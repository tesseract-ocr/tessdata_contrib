#!/usr/bin/env python3
"""
clean-corpus.py

Cleans and splits the Odia training corpus for Tesseract OCR training.

Rules applied:
  KEEP  — Odia Unicode block (U+0B00–U+0B7F), danda (।), double danda (॥),
           ZWNJ (U+200C for conjunct control), and space.
  STRIP — everything else: Hindu-Arabic numerals, Latin letters, all
           punctuation, symbols, currency signs, etc.
           Odia has its own numerals (୦-୯) in the Odia block.

After stripping, long lines are split into shorter segments at natural
Odia sentence boundaries (danda) or the nearest preceding space, so that
each corpus line stays under MAX_LINE_LEN characters. This gives cleaner
training images with less wrapping.

Run from ori-tesseract-training/:
  python3 corpus/clean-corpus.py
"""

import re
import shutil
from pathlib import Path

CORPUS  = Path(__file__).parent / "ori.training_text"
BACKUP  = Path(__file__).parent / "ori.training_text.bak"

# Split lines longer than this at a natural boundary
MAX_LINE_LEN = 150

# Keep only Odia block, dandas, ZWNJ, space
_STRIP = re.compile(r'[^଀-୿।॥‌ ]')
_SPACE = re.compile(r'  +')
_ODIA  = re.compile(r'[଀-୿]')


def strip_line(raw: str) -> str:
    s = _STRIP.sub(' ', raw.strip())
    return _SPACE.sub(' ', s).strip()


def split_at_boundary(text: str, max_len: int) -> list:
    """
    Split text into segments ≤ max_len chars, breaking at:
      1. Danda (।) or double danda (॥) — Odia sentence boundaries
      2. The last space before max_len — word boundary
    Each segment retains the danda that ended it.
    """
    # First split at every danda to get natural sentences
    parts = re.split(r'(?<=।)|(?<=॥)', text)
    segments = []
    current = ''

    for part in parts:
        part = part.strip()
        if not part:
            continue
        candidate = (current + ' ' + part).strip() if current else part
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                segments.append(current.strip())
            # part itself might still be too long — split at last space
            while len(part) > max_len:
                cut = part.rfind(' ', 0, max_len)
                if cut == -1:
                    cut = max_len  # no space found, hard cut
                segments.append(part[:cut].strip())
                part = part[cut:].strip()
            current = part

    if current.strip():
        segments.append(current.strip())

    return [s for s in segments if s]


def is_good(s: str) -> bool:
    odia_n  = len(_ODIA.findall(s))
    total_n = len(s.replace(' ', ''))
    return total_n > 0 and odia_n >= 5 and (odia_n / total_n) >= 0.85


def main():
    print("\n" + "━" * 54)
    print("  Cleaning Odia training corpus")
    print("━" * 54)

    with open(CORPUS, encoding="utf-8") as f:
        raw_lines = [l.rstrip("\n") for l in f if l.strip()]

    print(f"\n  Input lines : {len(raw_lines):,}")

    seen    = set()
    output  = []
    dropped = 0
    dupes   = 0
    splits  = 0

    for raw in raw_lines:
        cleaned = strip_line(raw)
        if not cleaned:
            dropped += 1
            continue

        # Split into shorter segments if needed
        segments = split_at_boundary(cleaned, MAX_LINE_LEN)
        if len(segments) > 1:
            splits += len(segments) - 1

        for seg in segments:
            if not is_good(seg):
                dropped += 1
                continue
            if seg in seen:
                dupes += 1
                continue
            seen.add(seg)
            output.append(seg)

    print(f"  Lines split into shorter segments: +{splits:,}")
    print(f"  Dropped (too short / not Odia)   : {dropped:,}")
    print(f"  Duplicates removed               : {dupes:,}")
    print(f"  Output lines                     : {len(output):,}")

    shutil.copy(CORPUS, BACKUP)
    print(f"\n  Backup: corpus/ori.training_text.bak")

    with open(CORPUS, "w", encoding="utf-8") as f:
        for line in output:
            f.write(line + "\n")

    print(f"  Wrote : corpus/ori.training_text")
    print("\n" + "━" * 54)
    print("  NEXT → ./01-generate-images.sh 10000")
    print("━" * 54 + "\n")


if __name__ == "__main__":
    main()
