import json
import random
from pathlib import Path

import pytest
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
REAL_ART_DIR = REPO / "assets" / "art"


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
