import re
import subprocess

import pytest

from carousel.errors import MusicNotFoundError
from carousel.music import load_music, music_credit, pick_music
from carousel.video import find_ffmpeg
from conftest import REAL_MUSIC_DIR


def test_load_music_reads_every_piece(music_dir):
    library = load_music(music_dir)
    assert sorted(library) == ["tone-a", "tone-b"]
    piece = library["tone-a"]
    assert (piece.title, piece.composer, piece.performer, piece.year) == ("Tone A", "Test Composer", "Test Player", "1916")
    assert piece.start == 0.5
    assert (music_dir / piece.file).exists()


def test_pick_music_is_stable_per_date_and_uses_the_whole_library(music_dir):
    library = load_music(music_dir)
    dates = [f"2026-11-{d:02d}" for d in range(1, 29)]
    picks = [pick_music(library, d).id for d in dates]
    assert picks == [pick_music(library, d).id for d in dates]
    assert set(picks) == {"tone-a", "tone-b"}


def test_requested_music_wins_over_the_default_pick(music_dir):
    library = load_music(music_dir)
    assert pick_music(library, "2026-11-23", requested="tone-b").id == "tone-b"
    assert pick_music(library, "2026-11-23", requested="tone-a").id == "tone-a"


def test_unknown_requested_music_raises(music_dir):
    with pytest.raises(MusicNotFoundError, match="zz9"):
        pick_music(load_music(music_dir), "2026-11-23", requested="zz9")


def test_credit_names_the_piece_the_composer_the_performer_the_year_and_the_licence(music_dir):
    assert music_credit(load_music(music_dir)["tone-a"]) == (
        "Music: Tone A, Test Composer, performed by Test Player, 1916. Public domain"
    )


def duration_seconds(path) -> float:
    info = subprocess.run([find_ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def test_real_music_library_is_complete_and_licensed():
    library = load_music(REAL_MUSIC_DIR)
    assert len(library) >= 8
    for piece in library.values():
        assert piece.license in ("CC0", "Public domain"), piece.id
        assert piece.source.startswith("https://archive.org/details/"), piece.id
        assert piece.composer.strip() and piece.performer.strip() and piece.year.strip(), piece.id
        assert duration_seconds(REAL_MUSIC_DIR / piece.file) >= piece.start + 15, piece.id
