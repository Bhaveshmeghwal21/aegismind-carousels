import json

import pytest
from PIL import Image

from carousel.errors import ArtNotFoundError
from carousel.library import credit_line, load_library, pick_art
from conftest import REAL_ART_DIR


def test_load_library_reads_every_piece(art_dir):
    library = load_library(art_dir)
    assert sorted(library) == ["a1", "b2"]
    piece = library["a1"]
    assert piece.title == "Piece a1"
    assert piece.focus == (0.5, 0.4)
    assert piece.vignette is None and piece.crop is None
    assert (art_dir / piece.file).exists()


def test_pick_art_is_stable_per_date_and_uses_the_whole_library(art_dir):
    library = load_library(art_dir)
    dates = [f"2026-11-{d:02d}" for d in range(1, 29)]
    picks = [pick_art(library, d).id for d in dates]
    assert picks == [pick_art(library, d).id for d in dates]
    assert set(picks) == {"a1", "b2"}


def test_requested_image_wins_over_the_default_pick(art_dir):
    library = load_library(art_dir)
    assert pick_art(library, "2026-11-23", requested="b2").id == "b2"
    assert pick_art(library, "2026-11-23", requested="a1").id == "a1"


def test_unknown_requested_image_raises(art_dir):
    with pytest.raises(ArtNotFoundError, match="zz9"):
        pick_art(load_library(art_dir), "2026-11-23", requested="zz9")


def test_credit_line_names_the_work_the_artist_the_date_and_the_museum(art_dir):
    line = credit_line(load_library(art_dir)["a1"])
    assert line == "Art: Piece a1, Unknown, c. 100 CE. The Cleveland Museum of Art, open access (CC0)"


def test_credit_line_skips_an_unknown_artist(art_dir):
    index = json.loads((art_dir / "index.json").read_text(encoding="utf-8"))
    index["a1"]["artist"] = ""
    (art_dir / "index.json").write_text(json.dumps(index), encoding="utf-8")
    assert credit_line(load_library(art_dir)["a1"]).startswith("Art: Piece a1, c. 100 CE.")


def test_real_library_is_complete_and_every_picture_opens():
    library = load_library(REAL_ART_DIR)
    assert len(library) >= 20
    for piece in library.values():
        assert piece.title.strip() and piece.date.strip(), piece.id
        assert piece.kind in ("photo", "ink"), piece.id
        assert all(0.0 <= v <= 1.0 for v in piece.focus), piece.id
        if piece.kind == "photo":
            assert "CC0" in piece.credit, piece.id
        else:
            assert "ink illustration" in piece.credit, piece.id
        with Image.open(REAL_ART_DIR / piece.file) as picture:
            assert min(picture.size) >= (1000 if piece.kind == "photo" else 900), piece.id


def test_credit_line_for_an_ink_illustration_has_no_artist(art_dir):
    index = json.loads((art_dir / "index.json").read_text(encoding="utf-8"))
    index["a1"].update(artist="", date="2026", credit="Original ink illustration, made with AI", kind="ink")
    (art_dir / "index.json").write_text(json.dumps(index), encoding="utf-8")
    piece = load_library(art_dir)["a1"]
    assert piece.kind == "ink" and load_library(art_dir)["b2"].kind == "photo"
    assert credit_line(piece) == "Art: Piece a1, 2026. Original ink illustration, made with AI"
