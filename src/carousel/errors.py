class UnsupportedGlyphError(ValueError):
    """Text contains a character the slide font cannot draw."""


class TextOverflowError(ValueError):
    """Text cannot fit on a slide even at the smallest allowed font size."""
