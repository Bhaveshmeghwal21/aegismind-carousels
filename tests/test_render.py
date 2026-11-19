from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageDraw, ImageStat

from carousel.errors import ArtNotFoundError, MusicNotFoundError, TextOverflowError, UnsupportedGlyphError
from carousel.models import Idea
from carousel.render import fit_quote, render_image, render_post

QUOTE = "Think lightly of yourself and deeply of the world."
TEXT_WHITE = 240


def grey_art(level: int = 90) -> Image.Image:
    return Image.new("RGB", (1080, 1350), (level, level, level))


def tones(img: Image.Image) -> set[tuple[int, int, int]]:
    return {c for _, c in img.convert("RGB").getcolors(maxcolors=2_000_000)}


def make_idea(date: str = "2026-11-23", **changes) -> Idea:
    fields = dict(date=date, status="ready", quote=QUOTE, author="Miyamoto Musashi", source="Dokkōdō (1645)")
    fields.update(changes)
    return Idea(**fields)


def test_post_is_1080x1350():
    assert render_image(QUOTE, "Miyamoto Musashi", grey_art()).size == (1080, 1350)


def test_only_black_white_and_grey_with_white_text():
    found = tones(render_image(QUOTE, "Miyamoto Musashi", grey_art()))
    assert all(r == g == b for r, g, b in found)
    assert (255, 255, 255) in found


def test_long_quote_never_enters_the_side_margins():
    img = render_image("word " * 40, "Someone", grey_art()).convert("L")
    assert img.crop((0, 0, 60, 1350)).getextrema()[1] < TEXT_WHITE
    assert img.crop((1020, 0, 1080, 1350)).getextrema()[1] < TEXT_WHITE


def test_text_gets_a_dark_scrim_even_over_bright_art():
    img = render_image("word " * 30, "Someone", grey_art(200)).convert("L")
    assert ImageStat.Stat(img.crop((0, 800, 60, 1150))).mean[0] < 110


def test_same_inputs_give_the_same_image():
    a = render_image(QUOTE, "Miyamoto Musashi", grey_art())
    b = render_image(QUOTE, "Miyamoto Musashi", grey_art())
    assert ImageChops.difference(a, b).getbbox() is None


def test_quote_lines_are_balanced_with_no_lone_last_word():
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    _, lines, _ = fit_quote("You test your own ideas the wrong way", 500, draw)
    assert len(lines) == 2
    assert all(len(line.split()) >= 3 for line in lines)


def test_a_short_quote_is_set_at_a_moderate_size():
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    font, lines, _ = fit_quote("Be here.", 500, draw)
    assert font.size <= 68 and len(lines) == 1


def test_curly_quotes_accents_dashes_render():
    text = "Nietzsche’s “abyss” — café, naïve"
    render_image(text, "Dokkōdō", grey_art())


def test_missing_glyph_in_quote_raises():
    with pytest.raises(UnsupportedGlyphError):
        render_image("漢字", "Someone", grey_art())


def test_missing_glyph_in_author_raises():
    with pytest.raises(UnsupportedGlyphError):
        render_image(QUOTE, "漢字", grey_art())


def test_quote_too_long_for_the_post_raises():
    with pytest.raises(TextOverflowError):
        render_image("word " * 2000, "Someone", grey_art())


def test_render_post_writes_the_image_and_the_caption(tmp_path: Path, art_dir: Path):
    paths = render_post(make_idea(image="b2", caption="Reflect."), tmp_path / "day", art_dir)
    assert paths == [tmp_path / "day" / "post.png"]
    assert Image.open(paths[0]).size == (1080, 1350)
    caption = (tmp_path / "day" / "caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("“Think lightly of yourself and deeply of the world.”\n— Miyamoto Musashi, Dokkōdō (1645)")
    assert "Art: Piece b2," in caption


def test_reel_option_writes_the_video_and_credits_the_music(tmp_path: Path, art_dir: Path, music_dir: Path):
    paths = render_post(make_idea(music="tone-b"), tmp_path / "day", art_dir, music_dir, reel_seconds=2)
    assert [p.name for p in paths] == ["post.png", "reel.mp4"]
    assert paths[1].exists()
    caption = (tmp_path / "day" / "caption.txt").read_text(encoding="utf-8")
    assert "Music: Tone B, Test Composer, performed by Test Player, 1916. Public domain" in caption


def test_without_a_reel_there_is_no_video_and_no_music_credit(tmp_path: Path, art_dir: Path, music_dir: Path):
    paths = render_post(make_idea(), tmp_path / "day", art_dir, music_dir)
    assert [p.name for p in paths] == ["post.png"]
    assert "Music:" not in (tmp_path / "day" / "caption.txt").read_text(encoding="utf-8")


def test_unknown_music_id_raises_and_writes_nothing(tmp_path: Path, art_dir: Path, music_dir: Path):
    with pytest.raises(MusicNotFoundError):
        render_post(make_idea(music="nope"), tmp_path / "x", art_dir, music_dir, reel_seconds=1)
    assert not (tmp_path / "x").exists()


def test_each_day_gets_its_own_art_and_a_rerun_matches(tmp_path: Path, art_dir: Path):
    (a,) = render_post(make_idea("2026-11-23"), tmp_path / "a", art_dir)
    (again,) = render_post(make_idea("2026-11-23"), tmp_path / "again", art_dir)
    assert a.read_bytes() == again.read_bytes()
    week = {render_post(make_idea(f"2026-11-{d}"), tmp_path / str(d), art_dir)[0].read_bytes() for d in range(23, 29)}
    assert len(week) == 6


def test_unknown_image_id_raises(tmp_path: Path, art_dir: Path):
    with pytest.raises(ArtNotFoundError):
        render_post(make_idea(image="nope"), tmp_path / "x", art_dir)
    assert not (tmp_path / "x").exists()
