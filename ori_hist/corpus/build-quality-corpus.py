#!/usr/bin/env python3
"""
build-quality-corpus.py

Builds corpus/ori.training_text from:
  Layer A — Advisory font-testing files (glyph coverage, kerning, spacing,
             conjuncts, all matra combinations, pangrams).
  Layer B — Wikipedia sentences from the cleaned backup corpus.

Rules applied:
  - Keep only: Odia Unicode block (U+0B00–U+0B7F), dandas (। ॥), space.
  - Lines capped at MAX_LINE_LEN chars, split at the last space before the cap.
  - Never split at colon or apostrophe (both are stripped anyway).
  - Minimum 3 Odia characters per line; minimum 85 % Odia ratio.
  - Deduplication across both layers.

Layer A comes first so ./01-generate-images.sh 10000 always exercises full
glyph coverage regardless of how many lines are rendered.
"""

import re
import sys
from pathlib import Path
from collections import Counter

VIRAMA        = '୍'
MAX_LINE      = 80     # target line length (Latin training data norm)
MAX_TOKEN_LEN = 30     # discard runaway mega-tokens from kerning tables
MIN_ODIA_N    = 3      # minimum Odia character count per line
MIN_RATIO     = 0.85   # minimum fraction of non-space chars that must be Odia

ADVISORY_DIR = Path('/Users/psubhashish/Documents/Text-Typography/'
                    'Chapakala/Chapakala19/AdvisoryCalls/forShubhashish')

CORPUS_DIR = Path(__file__).parent
NOISY      = CORPUS_DIR / 'ori.training_text.noisy'   # cleaned Wikipedia backup
OUTPUT     = CORPUS_DIR / 'ori.training_text'

# ── Character class patterns ───────────────────────────────────────────────
_STRIP = re.compile(r'[^଀-୿।॥ ]')  # strip non-Odia
_MULTI = re.compile(r' {2,}')
_ODIA  = re.compile(r'[଀-୿]')


# ── Helpers ────────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    """Strip everything except Odia block, dandas, space; collapse runs."""
    s = _STRIP.sub(' ', text)
    return _MULTI.sub(' ', s).strip()


def is_good(line: str) -> bool:
    odia_n  = len(_ODIA.findall(line))
    total_n = len(line.replace(' ', ''))
    return total_n > 0 and odia_n >= MIN_ODIA_N and (odia_n / total_n) >= MIN_RATIO


def virama_count(tok: str) -> int:
    return tok.count(VIRAMA)


def split_at_space(text: str, max_len: int) -> list:
    """Split a long string into segments ≤ max_len at the last space before cap."""
    segs = []
    while len(text) > max_len:
        cut = text.rfind(' ', 0, max_len)
        if cut == -1:
            cut = max_len  # no space: hard cut (rare for Odia tokens)
        seg = text[:cut].strip()
        if seg:
            segs.append(seg)
        text = text[cut:].strip()
    if text:
        segs.append(text)
    return segs


def pack_tokens(tokens: list, max_len: int) -> list:
    """
    Pack space-delimited tokens into lines of ≤ max_len chars.
    Never splits inside a token.
    """
    lines, current = [], ''
    for tok in tokens:
        if not tok:
            continue
        candidate = (current + ' ' + tok).strip() if current else tok
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                lines.append(current)
            # Token itself may exceed max_len — hard-split it
            while len(tok) > max_len:
                lines.append(tok[:max_len])
                tok = tok[max_len:]
            current = tok
    if current:
        lines.append(current)
    return lines


def tokens_from_file(path: Path) -> list:
    """Extract every Odia token from an advisory file, skipping comment lines."""
    tokens = []
    try:
        with open(path, encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if line.startswith('#') or not line:
                    continue
                cleaned = clean(line)
                if not cleaned:
                    continue
                # Split on spaces and dandas; keep non-empty tokens within
                # a reasonable length (kerning tables concatenate chars with
                # matra-A separators that survive the strip pass)
                parts = re.split(r'[ ।॥]+', cleaned)
                tokens.extend(t for t in parts if t and len(t) <= MAX_TOKEN_LEN)
    except OSError as e:
        print(f'  WARNING: cannot read {path.name}: {e}', file=sys.stderr)
    return tokens


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print()
    print('━' * 56)
    print('  Building quality Odia training corpus')
    print('━' * 56)

    # ── Layer A: advisory files ────────────────────────────────────────
    # Token sources: properly spaced — each space-delimited cluster is one token.
    token_files = [
        ADVISORY_DIR / '02_TextSamples.txt',
        ADVISORY_DIR / '03_Glyphset.txt',
        ADVISORY_DIR / '04_ExhaustiveTestcase.txt',
    ]
    # Line sources: Kerning.txt / Spacing.txt have concatenated char sequences
    # with no spaces (digit+matra pairs, spacing test runs).  We treat each
    # non-comment line as a corpus entry and split at MAX_LINE chars.
    line_source_files = [
        ADVISORY_DIR / 'Kerning.txt',
        ADVISORY_DIR / 'Spacing.txt',
    ]

    all_tokens = []
    print('\n  Layer A — advisory files (token sources)')
    for af in token_files:
        toks = tokens_from_file(af)
        print(f'    {af.name:<35} {len(toks):>6} tokens')
        all_tokens.extend(toks)

    # Deduplicate while preserving first-seen order
    seen_tok: set = set()
    unique_tokens = []
    for t in all_tokens:
        if t not in seen_tok:
            seen_tok.add(t)
            unique_tokens.append(t)

    print(f'    {"Unique tokens total":<35} {len(unique_tokens):>6}')

    # ── Virama analysis ────────────────────────────────────────────────
    vc = Counter({t: virama_count(t) for t in unique_tokens if virama_count(t) > 0})
    max_v  = vc.most_common(1)[0][1] if vc else 0
    top_v  = [t for t, c in vc.items() if c == max_v]
    print()
    print(f'  Virama analysis')
    print(f'    Maximum viramas in one token : {max_v}')
    print(f'    Count of such tokens         : {len(top_v)}')
    print(f'    Examples (first 8)           : {" ".join(top_v[:8])}')

    # Sort tokens: most-virama-rich first so the first rendered pages cover
    # the hardest conjunct sequences the model needs to learn.
    sorted_tokens = sorted(unique_tokens, key=lambda t: -virama_count(t))

    advisory_lines = pack_tokens(sorted_tokens, MAX_LINE)
    advisory_lines = [l for l in advisory_lines if is_good(l)]

    # Add lines from kerning/spacing files (concatenated char sequences)
    kerning_lines = []
    print('\n  Layer A — line sources (kerning, spacing)')
    for lf in line_source_files:
        count = 0
        try:
            with open(lf, encoding='utf-8') as f:
                for raw in f:
                    line = raw.strip()
                    if line.startswith('#') or not line:
                        continue
                    cleaned = clean(line)
                    if not cleaned:
                        continue
                    for seg in split_at_space(cleaned, MAX_LINE):
                        if is_good(seg):
                            kerning_lines.append(seg)
                            count += 1
        except OSError as e:
            print(f'  WARNING: {lf.name}: {e}', file=sys.stderr)
        print(f'    {lf.name:<35} {count:>6} lines')

    advisory_lines = advisory_lines + kerning_lines
    print(f'\n    Total advisory lines (packed at {MAX_LINE} chars): {len(advisory_lines):,}')

    # ── Layer B: Wikipedia sentences from cleaned backup ───────────────
    wiki_lines = []
    if NOISY.exists():
        print(f'\n  Layer B — {NOISY.name}')
        with open(NOISY, encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if not is_good(line):
                    continue
                # Re-split from 150-char cap to MAX_LINE
                for seg in split_at_space(line, MAX_LINE):
                    if is_good(seg):
                        wiki_lines.append(seg)
        print(f'    Wikipedia lines (re-split to {MAX_LINE} chars): {len(wiki_lines):,}')
    else:
        print(f'\n  WARNING: {NOISY} not found — corpus will be advisory-only.')

    # ── Merge & deduplicate ────────────────────────────────────────────
    seen_line: set = set()
    output = []

    for line in advisory_lines:
        if line not in seen_line:
            seen_line.add(line)
            output.append(line)

    for line in wiki_lines:
        if line not in seen_line:
            seen_line.add(line)
            output.append(line)

    # ── Stats ──────────────────────────────────────────────────────────
    avg_len = sum(len(l) for l in output) / len(output) if output else 0
    max_len = max(len(l) for l in output) if output else 0
    min_len = min(len(l) for l in output) if output else 0

    print()
    print('  ── Output stats ──────────────────────────────────────')
    print(f'    Total lines  : {len(output):,}')
    print(f'    Avg length   : {avg_len:.0f} chars')
    print(f'    Max length   : {max_len} chars')
    print(f'    Min length   : {min_len} chars')
    print(f'    Advisory     : {len(advisory_lines):,} lines (first in file)')
    print(f'    Wikipedia    : {len(output) - len(advisory_lines):,} lines')

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        for line in output:
            f.write(line + '\n')

    print()
    print(f'  Wrote: corpus/ori.training_text')
    print()
    print('  Max-virama tokens (full list of longest conjuncts):')
    for t in top_v:
        print(f'    {t}  ({max_v} viramas)')
    print()
    print('━' * 56)
    print(f'  NEXT → ./01-generate-images.sh 10000')
    print('━' * 56)
    print()


if __name__ == '__main__':
    main()
