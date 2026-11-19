import json
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageDraw

from carousel.errors import TextOverflowError, UnsupportedGlyphError
from carousel.ink import load_ink_art, render_ink_image, short_source
from carousel.library import load_library
from carousel.models import Idea
from carousel.render import render_post

QUOTE = "Think lightly of yourself and deeply of the world."


@pytest.fixture
def ink_dir(tmp_path: Path) -> Path:
    """A one-picture ink library: a black figure on slightly off-white paper."""
    folder = tmp_path / "ink"
    folder.mkdir()
    picture = Image.new("L", (1280, 960), 246)
    ImageDraw.Draw(picture).ellipse([440, 200, 840, 900], fill=10)
    picture.save(folder / "figure.png")
    entry = {
        "title": "Test figure", "artist": "", "date": "2026", "credit": "Original ink illustration, made with AI",
        "file": "figure.png", "focus": [0.5, 0.45], "gamma": 1.0, "vignette": None, "crop": None, "kind": "ink",
    }
    (folder / "index.json").write_text(json.dumps({"figure": entry}), encoding="utf-8")
    return folder


def piece_art(ink_dir: Path):
    piece = load_library(ink_dir)["figure"]
    return piece, load_ink_art(piece, ink_dir)


def test_short_source_drops_the_translator_and_a_trailing_year():
    assert short_source("Meditations 5.16, tr. George Long") == "Meditations 5.16"
    assert short_source("Dokkōdō (1645)") == "Dokkōdō"
    assert short_source("Dhammapada, verse 1, tr. F. Max Müller (1881)") == "Dhammapada, verse 1"
    assert short_source("Plato, Apology 38a") == "Plato, Apology 38a"
    assert short_source("") == ""


def test_art_paper_becomes_pure_white(ink_dir: Path):
    _, art = piece_art(ink_dir)
    assert art.getpixel((5, 5)) == 255
    assert art.getpixel((640, 500)) < 40


def test_post_is_1080x1350_with_black_text_on_a_white_page(ink_dir: Path):
    piece, art = piece_art(ink_dir)
    img = render_ink_image(QUOTE, "Miyamoto Musashi", "Dokkōdō (1645)", art, piece.focus)
    assert img.size == (1080, 1350)
    grey = img.convert("L")
    assert grey.getpixel((2, 2)) == 255 and grey.getpixel((1077, 20)) == 255
    assert grey.crop((0, 0, 1080, 380)).getextrema() == (0, 255)  # the text is there, pure black on pure white
    assert all(r == g == b for r, g, b in [img.getpixel(p) for p in [(100, 100), (540, 100), (540, 900)]])


def test_illustration_fills_the_lower_part_of_the_page(ink_dir: Path):
    piece, art = piece_art(ink_dir)
    img = render_ink_image(QUOTE, "Miyamoto Musashi", "Dokkōdō (1645)", art, piece.focus).convert("L")
    assert img.getpixel((540, 1000)) < 40


def test_longest_quote_still_fits_and_keeps_most_of_the_picture(ink_dir: Path):
    piece, art = piece_art(ink_dir)
    long_quote = "word " * 27  # about 140 characters
    img = render_ink_image(long_quote, "A Very Long Philosophers Name", "Some Work, 1.2.3, tr. Someone (1900)", art, piece.focus).convert("L")
    assert img.getpixel((540, 1000)) < 40
    assert img.crop((0, 0, 60, 1350)).getextrema()[0] == 255  # text never enters the side margins


def test_same_inputs_give_the_same_image(ink_dir: Path):
    piece, art = piece_art(ink_dir)
    a = render_ink_image(QUOTE, "Seneca", "Letters 13", art, piece.focus)
    b = render_ink_image(QUOTE, "Seneca", "Letters 13", art, piece.focus)
    assert ImageChops.difference(a, b).getbbox() is None


def test_text_that_cannot_fit_raises(ink_dir: Path):
    piece, art = piece_art(ink_dir)
    with pytest.raises(TextOverflowError):
        render_ink_image("word " * 200, "Someone", "", art, piece.focus)


def test_unsupported_glyph_raises(ink_dir: Path):
    piece, art = piece_art(ink_dir)
    with pytest.raises(UnsupportedGlyphError):
        render_ink_image("心", "Someone", "", art, piece.focus)


def test_render_post_uses_the_ink_layout_and_a_light_reel(tmp_path: Path, ink_dir: Path, music_dir: Path):
    idea = Idea(date="2026-11-24", status="ready", quote=QUOTE, author="Miyamoto Musashi", source="Dokkōdō (1645)", image="figure", music="tone-a")
    paths = render_post(idea, tmp_path / "out", ink_dir, music_dir, reel_seconds=2)
    assert [p.name for p in paths] == ["post.png", "reel.mp4"]
    assert Image.open(paths[0]).convert("L").getpixel((2, 2)) == 255  # white page, not the dark photo look
    caption = (tmp_path / "out" / "caption.txt").read_text(encoding="utf-8")
    assert "Art: Test figure, 2026. Original ink illustration, made with AI" in caption
