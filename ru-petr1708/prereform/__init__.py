"""Tools for OCRing pre-reform Russian print.

Five independent pieces, usable separately:

    lexicon    the ru_petr1708 word list as a set, and hit rate as a metric
    image      background normalisation, which is what makes scans readable
    glyph      the three-legged te of pre-1850 civil type, measured not guessed
    repair     lexicon-gated correction of what the model still gets wrong
    quality    is this page text, noise, or a blank leaf

Nothing here imports anything else here except through explicit arguments, so
a caller who wants only the te measurement need not have a word list.
"""
__all__ = ['lexicon', 'image', 'glyph', 'repair', 'quality']
