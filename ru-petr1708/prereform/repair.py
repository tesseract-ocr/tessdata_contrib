"""Lexicon-gated repair of the errors the model still makes after the glyph pass.

A repair driven by a word list can raise its own score by destroying the thing
it was meant to preserve. Turn a name that is in no word list into the nearest
word that is, and the dictionary hit rate goes up while the onomasticon goes
down; the metric counts a ruined name as a success. Everything in this module
is arranged around not doing that, and the four guards below were each put in
after watching the pass do the damage they prevent.

The pass touches a token only when it is not itself a word and the confusable
letters admit exactly one reading that is. Candidates are generated over all
confusions at once rather than one rule at a time, so a token readable two ways
is seen to be ambiguous and left alone: удѣлъ is both a locative and a
nominative and is therefore never guessed at.
"""
import re, itertools

TOKEN = re.compile(r'[\u0400-\u04FF]+')
CYR = re.compile(r'[\u0400-\u04FF]+')


def _cased(d):
    d = dict(d)
    d.update({k.upper(): tuple(v.upper() for v in vs) for k, vs in d.items()})
    return d


# Orthographic confusions. These fall on endings -- the breve of i-short read
# for the dot of i-decimal, the hard sign and yat reduced to a soft sign -- so
# they change how a word is spelled, not which word it is.
ORTHO = _cased({'й': ('і',), 'ь': ('ъ', 'ѣ')})

# Shape confusions: the three-legged te and its neighbours. These fall on stems,
# and a stem is what distinguishes one name from another.
SHAPE = _cased({'ш': ('т', 'п'), 'п': ('т',), 'т': ('ш', 'п')})

CONFUSE = {**ORTHO, **SHAPE}

# GUARD 1. Below four letters the lexicon stops being evidence. Nearly every
# three-letter Cyrillic string is some inflected form among 1.4M of them, so a
# short piece of OCR noise always has a reading and the uniqueness test cannot
# reject it: this produced сти -> спи and томъ -> помъ. The short words that
# are genuinely damaged are function words whose sense survives the error.
MINLEN = 4

HYPHEN = re.compile(r'([\u0400-\u04FF]{2,})[-\u2010\u2013\u2014][ \t]*\n[ \t]*'
                    r'([\u0430-\u045F\u0450-\u045F][\u0400-\u04FF]+)')

# GUARD 2. No '^' in HEAD: re.match(s, pos) anchors at pos by itself, whereas
# '^' would still only match at the true start of the string.
TAIL = re.compile(r'[-\u2010\u2013\u2014][ \t]*\n')
HEAD = re.compile(r'[-\u2010\u2013\u2014][ \t]*\n[ \t]*$')

# GUARD 4. Prepositions governing the locative, with final hard and soft signs
# stripped, because the OCR gives 'Въь' for 'Въ' often enough to matter.
LOC_PREP = {'в', 'во', 'на', 'о', 'об', 'при', 'по'}


def dehyphenate(txt):
    """Rejoin words broken across a line by a trailing hyphen.

    Roughly one token in seven is a fragment in this material, and a fragment is
    not a word, so leaving them split both understates any lexical measurement
    and invites the repair below to 'correct' half a word into a whole one.
    Only lowercase continuations are joined: the capitalised ones are running
    heads and catchwords that collided with the text, not real breaks.
    """
    return HYPHEN.subn(r'\1\2', txt)


def readings(t, vocab, shape, maxsub=3):
    """Every word `t` could be under at most `maxsub` letter swaps.

    GUARD 3. A capitalised token is read as a proper name and only its spelling
    is allowed to change. The word list holds no names at all, so a name is
    always a non-word with a plausible reading nearby, and letting stems move
    turns Ютка into Юшка and Паня into Таня -- which in an onomasticon destroys
    precisely the entry the book exists to record.
    """
    table = CONFUSE if shape and not t[:1].isupper() else ORTHO
    pos = [i for i, c in enumerate(t) if c in table]
    out = set()
    for r in range(1, min(len(pos), maxsub) + 1):
        for combo in itertools.combinations(pos, r):
            for repl in itertools.product(*(table[t[i]] for i in combo)):
                v = list(t)
                for i, c in zip(combo, repl):
                    v[i] = c
                v = ''.join(v)
                if v in vocab or v.lower() in vocab:
                    out.add(v)
    return out


def governs_locative(txt, start, back=2):
    """Does a preposition taking the locative stand just before this token?"""
    return any(p.lower().rstrip('ъь') in LOC_PREP
               for p in CYR.findall(txt[max(0, start - 60):start])[-back:])


def adds_final_yat(t, v):
    """Does this reading put a yat on the end that the page does not have?

    Only the final letter is asked about, and the position is the whole point.
    A yat inside a word is spelling and is always safe -- Льтописи for Лѣтописи
    was 209 of the repairs in one index alone -- but a yat in final position is
    a locative ending, and supplying one changes the grammatical form rather
    than the spelling of the word.
    """
    return v[-1:] in ('ѣ', 'Ѣ') and t[-1:] not in ('ѣ', 'Ѣ')


def lexical_pass(txt, vocab, shape=False):
    """Repair residual glyph errors where the lexicon is unambiguous.

    `shape` enables the stem repairs and is meant to be set from the glyph
    measurement rather than by hand: pass glyph.te_share(fixed, kept) > 0.15.
    Where a book does not set the three-legged te there is nothing for the stem
    repairs to fix, and they only misread тинъ as шинъ and четь, a real land
    measure absent from the word list, as чешь.

    Half-words are skipped. Whatever dehyphenate declined to join is a fragment,
    and a fragment is not a word, so it would otherwise be 'repaired' into the
    nearest thing that is: ТВО, the front of ТВОЕГО, becomes ПВО, which is in
    the word list because the list is not in fact confined to pre-reform forms.

    A capitalised token is additionally refused a final yat unless a preposition
    governs one. Yat and soft sign differ by a crossbar and are freely confused,
    so the reading is always available, and on a name it is not a spelling but a
    case: name lists run Тудьрь, Туль, Хрель, Хрьсо, every member ending in a
    soft sign, and reading one of them as a locative fabricates a form the page
    does not have. Where the case is licensed -- въ Москвѣ, по Пасхѣ -- the
    same repair is right and is still made.

    Withdrawing those fabricated locatives also restores correct nominatives,
    which is worth expecting rather than being surprised by: with the yat
    candidate gone, the hard-sign reading becomes the unique one and passes the
    test it had been failing. Over six books this withdrew 41 wrong forms and
    restored 702 right ones -- Воинъ, Трофимъ, Беркутъ, Булатъ, Кречетъ.
    """
    changed = 0

    def fix(m):
        nonlocal changed
        t = m.group(0)
        if len(t) < MINLEN or t in vocab or t.lower() in vocab:
            return t
        if TAIL.match(txt, m.end()) or HEAD.search(txt, max(0, m.start() - 12),
                                                  m.start()):
            return t
        cands = readings(t, vocab, shape)
        if t[:1].isupper() and not governs_locative(txt, m.start()):
            cands = {v for v in cands if not adds_final_yat(t, v)}
        if len(cands) == 1:
            changed += 1
            return cands.pop()
        return t

    return TOKEN.sub(fix, txt), changed
