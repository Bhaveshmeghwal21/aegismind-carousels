"""The art library: public-domain pictures in assets/art with how to frame and grade each one."""

import json
import zlib
from dataclasses import dataclass
from pathlib import Path

from .errors import ArtNotFoundError

DEFAULT_ART_DIR = Path(__file__).resolve().parents[2] / "assets" / "art"


@dataclass(frozen=True)
class ArtPiece:
    id: str
    title: str
    artist: str  # empty when unknown
    date: str
    credit: str
    file: str  # file name inside the art directory
    focus: tuple[float, float]  # where the subject sits in the picture, as fractions (x, y)
    gamma: float  # above 1.0 makes the picture darker
    vignette: tuple[float, float, float, float, float] | None  # (cx, cy, rx, ry, floor) on the 1080x1350 canvas
    crop: tuple[float, float, float, float] | None  # (left, top, right, bottom) fractions to keep


def load_library(art_dir: Path = DEFAULT_ART_DIR) -> dict[str, ArtPiece]:
    raw = json.loads((Path(art_dir) / "index.json").read_text(encoding="utf-8"))
    return {
        art_id: ArtPiece(
            id=art_id,
            title=entry["title"],
            artist=entry.get("artist", ""),
            date=entry["date"],
            credit=entry["credit"],
            file=entry["file"],
            focus=tuple(entry["focus"]),
            gamma=entry.get("gamma", 1.3),
            vignette=tuple(entry["vignette"]) if entry.get("vignette") else None,
            crop=tuple(entry["crop"]) if entry.get("crop") else None,
        )
        for art_id, entry in raw.items()
    }


def pick_art(library: dict[str, ArtPiece], date: str, requested: str | None = None) -> ArtPiece:
    """The requested piece, or one chosen by the date so a rerun gives the same picture."""
    if requested:
        if requested not in library:
            raise ArtNotFoundError(f"image {requested!r} is not in the art library")
        return library[requested]
    ids = sorted(library)
    return library[ids[zlib.crc32(date.encode()) % len(ids)]]


def credit_line(piece: ArtPiece) -> str:
    parts = [piece.title] + ([piece.artist] if piece.artist else []) + [piece.date]
    return f"Art: {', '.join(parts)}. {piece.credit}"
