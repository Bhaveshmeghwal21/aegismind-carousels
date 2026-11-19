import json
import random
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from carousel.video import find_ffmpeg

REPO = Path(__file__).resolve().parents[1]
REAL_ART_DIR = REPO / "assets" / "art"
REAL_MUSIC_DIR = REPO / "assets" / "music"


def piece_entry(file: str, **overrides) -> dict:
    entry = {
        "title": "Test Head",
        "artist": "Unknown",
        "date": "c. 100 CE",
        "credit": "The Cleveland Museum of Art, open access (CC0)",
        "file": file,
        "focus": [0.5, 0.4],
        "gamma": 1.3,
        "vignette": None,
        "crop": None,
    }
    entry.update(overrides)
    return entry


@pytest.fixture
def art_dir(tmp_path: Path) -> Path:
    """A tiny art library of two noisy greyscale test pictures, so tests never touch the real art."""
    folder = tmp_path / "art"
    folder.mkdir()
    rng = random.Random(0)
    index = {}
    for name, floor in (("a1", 100), ("b2", 60)):
        picture = Image.frombytes("L", (600, 800), rng.randbytes(600 * 800)).point(lambda v, f=floor: f + v // 3)
        picture.save(folder / f"{name}.jpg", quality=92)
        index[name] = piece_entry(f"{name}.jpg", title=f"Piece {name}")
    (folder / "index.json").write_text(json.dumps(index), encoding="utf-8")
    return folder


def make_tone(path: Path, frequency: int, seconds: int = 20) -> None:
    subprocess.run(
        [find_ffmpeg(), "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency={frequency}:duration={seconds}", "-c:a", "aac", str(path)],
        check=True,
    )


@pytest.fixture
def music_dir(tmp_path: Path) -> Path:
    """Two synthetic tone clips with an index, so tests never touch the real recordings."""
    folder = tmp_path / "music"
    folder.mkdir()
    index = {}
    for name, frequency in (("tone-a", 220), ("tone-b", 330)):
        make_tone(folder / f"{name}.m4a", frequency)
        index[name] = {
            "title": f"Tone {name[-1].upper()}",
            "composer": "Test Composer",
            "performer": "Test Player",
            "year": "1916",
            "license": "Public domain",
            "source": "https://archive.org/details/test",
            "file": f"{name}.m4a",
            "start": 0.5,
        }
    (folder / "index.json").write_text(json.dumps(index), encoding="utf-8")
    return folder
