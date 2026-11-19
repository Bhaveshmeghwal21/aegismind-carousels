"""The music library: short clips of public-domain recordings in assets/music, baked into the Reel."""

import json
import zlib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .errors import MusicNotFoundError

DEFAULT_MUSIC_DIR = Path(__file__).resolve().parents[2] / "assets" / "music"


@dataclass(frozen=True)
class MusicPiece:
    id: str
    title: str
    composer: str
    performer: str
    year: str  # when the recording was made or released
    license: str  # "CC0", "Public domain" or "CC BY 4.0" (needs the credit music_credit writes)
    source: str  # where the recording was found (and its licence can be checked)
    file: str  # clip file name inside the music directory
    start: float  # seconds into the clip where playback begins


def load_music(music_dir: Path = DEFAULT_MUSIC_DIR) -> dict[str, MusicPiece]:
    raw = json.loads((Path(music_dir) / "index.json").read_text(encoding="utf-8"))
    return {
        music_id: MusicPiece(
            id=music_id,
            title=entry["title"],
            composer=entry["composer"],
            performer=entry["performer"],
            year=entry["year"],
            license=entry["license"],
            source=entry["source"],
            file=entry["file"],
            start=float(entry.get("start", 0.0)),
        )
        for music_id, entry in raw.items()
    }


def pick_music(library: dict[str, MusicPiece], date: str, requested: str | None = None) -> MusicPiece:
    """The requested piece, or one chosen by the date so a rerun gives the same music."""
    if requested:
        if requested not in library:
            raise MusicNotFoundError(f"music {requested!r} is not in the music library")
        return library[requested]
    ids = sorted(library)
    return library[ids[zlib.crc32(date.encode()) % len(ids)]]


def music_credit(piece: MusicPiece) -> str:
    if piece.license.upper().startswith("CC BY"):
        # Creative Commons attribution: title, author, where to find it, the licence, and a note that it was edited
        site = urlparse(piece.source).netloc.removeprefix("www.")
        return f'Music: "{piece.title}" by {piece.composer} ({site}), {piece.license}. Shortened and faded.'
    return f"Music: {piece.title}, {piece.composer}, performed by {piece.performer}, {piece.year}. {piece.license}"
