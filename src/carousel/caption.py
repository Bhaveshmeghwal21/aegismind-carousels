from .library import ArtPiece, credit_line
from .models import Idea

OPENING_MARKS, CLOSING_MARKS = '"“', '"”'


def display_quote(text: str) -> str:
    """The quote in curly quotation marks, without doubling marks already there."""
    text = text.strip()
    if len(text) > 1 and text[0] in OPENING_MARKS and text[-1] in CLOSING_MARKS:
        text = text[1:-1].strip()
    return f"“{text}”"


def build_caption(idea: Idea, piece: ArtPiece) -> str:
    """Quote and attribution, the reflection, the art credit, then hashtags. Empty parts are left out."""
    attribution = f"— {idea.author}" + (f", {idea.source}" if idea.source else "")
    parts = [f"{display_quote(idea.quote)}\n{attribution}", idea.caption, credit_line(piece), idea.tags]
    return "\n\n".join(part for part in parts if part)
