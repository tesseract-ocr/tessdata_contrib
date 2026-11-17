"""The ru_petr1708 word list, as a lookup set and as a measurement.

ru_petr1708 is a Hunspell dictionary of Russian in the orthography used between
Peter's civil-type reform of 1708 and the reform of 1918: yat, i-decimal, fita,
izhitsa and the word-final hard sign are all present. It is the only large
machine-readable list of the orthography this material is printed in, which is
what makes it useful twice over -- once as a dictionary compiled into the OCR
model, and once as an outside check on the OCR that model produces.

The hit rate is worth more than tesseract's own confidence because it is
independent of the recogniser. A model asked to read pre-reform type with a
post-reform character set is confident and wrong: it reports high confidence on
`свът` because `ъ` is a letter it knows, while `свѣтъ` is not a string it can
emit at all. The word list notices; the confidence score does not.

The metric has one blind spot worth stating. The list is inflected forms of
common words and holds no proper names, so a page of an onomasticon scores low
however well it was read. Use the hit rate to compare two readings of the same
page, not to compare two pages.
"""
import os, re, functools

# The upstream distribution is kept whole rather than having the two files
# lifted out of it, so that the dictionary stays next to its LICENSE.txt and
# the version it came from stays legible in the path.
DIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'ru-petr1708-hunspell-3.1', 'ru_petr1708', 'ru_petr1708.dic')

# Three letters is the floor at which a Cyrillic string carries any evidence at
# all; see repair.MINLEN for the same threshold applied to a different purpose.
TOKEN = re.compile(r'[\u0400-\u04FF]{3,}')


@functools.lru_cache(maxsize=4)
def words(dic=None):
    """Every surface form in the list, in the case given and in lower case.

    Hunspell's first line is the entry count, and an entry is `form/FLAGS`.

    In this dictionary the flags never appear: the .aff defines no SFX or PFX
    rules and not one of the 1430220 entries carries a flag, so the file is a
    flat list of surface forms already inflected. The split on '/' is kept
    because it costs nothing and makes the reader work on a .dic that does use
    flags -- but on such a file it takes the stems only, and the affixes would
    have to be expanded separately.
    """
    out = set()
    with open(dic or DIC, encoding='utf-8') as f:
        f.readline()
        for line in f:
            w = line.strip().split('/')[0]
            if w:
                out.add(w)
                out.add(w.lower())
    return frozenset(out)


def contains(vocab, token):
    """Is this token a word, tried as printed and in lower case?"""
    return token in vocab or token.lower() in vocab


def hit_rate(txt, vocab=None):
    """(share of Cyrillic tokens that are real pre-reform words, token count).

    Returns 0.0 on a text with no Cyrillic in it, which is the honest answer:
    a reading with nothing to score is not a good reading.
    """
    vocab = vocab if vocab is not None else words()
    toks = TOKEN.findall(txt)
    if not toks:
        return 0.0, 0
    return sum(1 for t in toks if contains(vocab, t)) / len(toks), len(toks)
