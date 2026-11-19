from .library import ArtPiece, credit_line
from .models import Idea
from .music import MusicPiece, music_credit

OPENING_MARKS, CLOSING_MARKS = '"“', '"”'


def display_quote(text: str) -> str:
    """The quote in curly quotation marks, without doubling marks already there."""
    text = text.strip()
    if len(text) > 1 and text[0] in OPENING_MARKS and text[-1] in CLOSING_MARKS:
        text = text[1:-1].strip()
    return f"“{text}”"


def build_caption(idea: Idea, piece: ArtPiece, track: MusicPiece | None = None) -> str:
    """Quote and attribution, the reflection, the art and music credits, then hashtags. Empty parts are left out."""
    attribution = f"— {idea.author}" + (f", {idea.source}" if idea.source else "")
    credits = credit_line(piece) + (f"\n{music_credit(track)}" if track else "")
    parts = [f"{display_quote(idea.quote)}\n{attribution}", idea.caption, credits, idea.tags]
    return "\n\n".join(part for part in parts if part)
