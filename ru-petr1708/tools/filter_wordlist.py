#!/usr/bin/env python3
"""Reduce a Hunspell .dic to the forms a given tesseract unicharset can emit.

wordlist2dawg will not silently drop a word containing a character the model
has no code for; it stops. So the list has to be filtered against the model's
own unicharset first, and the filtering is not merely mechanical -- it is where
you find out what the model cannot represent.

For orus this removes 2130 of 1430220 entries, and reading what was removed is
the point: they are the words spelled with fita and izhitsa. The model has no
code for either, so no dictionary can teach it to produce them, and every
Ѳеодоръ in the corpus will be read as Феодоръ. That is a limitation to record
in the output, not one to be discovered later by a reader.

Two further reductions follow, and both change the compiled dawg, so they are
part of the specification of the build rather than tidying. Duplicate forms are
dropped, and so are single letters: see MINLEN.

    python3 filter_wordlist.py ru_petr1708.dic orus.lstm-unicharset out.txt
"""
import sys

# A one-letter entry would make every isolated letter a dictionary word, and a
# scanned page is full of isolated letters that are not words -- specks, broken
# type, the tail of a word the line-finder cut. The .dic carries six of them
# (а и о у э я).
MINLEN = 2


def unicharset(path):
    """The single characters a model can emit.

    Line 1 is the entry count; thereafter the first field is the character.
    Multi-character entries are ligatures and are not useful for filtering,
    since a word is checked one character at a time.
    """
    with open(path, encoding='utf-8') as f:
        f.readline()
        return {l.split(' ')[0] for l in f if l.strip()
                and len(l.split(' ')[0]) == 1}


def dic_forms(path):
    """Surface forms from a Hunspell .dic: first line is a count, flags follow '/'."""
    with open(path, encoding='utf-8') as f:
        f.readline()
        for line in f:
            w = line.strip().split('/')[0]
            if w:
                yield w


def main(dic, uni, out):
    """Filter, deduplicate, and drop single letters, in that order.

    Order of the last two does not matter, but doing them at all does.
    wordlist2dawg is not insensitive to either: repeating a word or adding a
    one-letter one changes the compiled bytes, so a build that skips these
    steps produces a different dawg from the one described here.
    """
    ok = unicharset(uni)
    kept, dropped, seen = [], [], set()
    total = dup = short = 0
    for w in dic_forms(dic):
        total += 1
        if not set(w) <= ok:
            dropped.append(w)
        elif w in seen:
            dup += 1
        else:
            seen.add(w)
            if len(w) < MINLEN:
                short += 1
            else:
                kept.append(w)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(kept) + '\n')

    missing = sorted({c for w in dropped for c in w} - ok)
    print(f'kept {len(kept)} of {total}')
    print(f'    {len(dropped)} unrepresentable, {dup} duplicate, '
          f'{short} single letter')
    print(f'characters the model cannot represent: {"".join(missing)}')
    for c in missing:
        n = sum(1 for w in dropped if c in w)
        print(f'   {c!r} U+{ord(c):04X}  in {n} entries')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
