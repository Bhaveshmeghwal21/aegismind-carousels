class IdeaParseError(ValueError):
    """An entry in an ideas file is missing a field or is malformed."""


class UnsupportedGlyphError(ValueError):
    """Text contains a character the slide font cannot draw."""


class TextOverflowError(ValueError):
    """Text cannot fit on a slide even at the smallest allowed font size."""


class ArtNotFoundError(ValueError):
    """An idea asked for an art id that is not in the art library."""


class MusicNotFoundError(ValueError):
    """An idea asked for a music id that is not in the music library."""
