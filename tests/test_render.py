from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageDraw, ImageStat

from carousel.errors import TextOverflowError, UnsupportedGlyphError
from carousel.models import Idea
from carousel.render import fit_hook, render_image, render_post

HOOK = "Marcus Aurelius rehearsed bad days every morning"
TEXT_WHITE = 240


def tones(img: Image.Image) -> set[tuple[int, int, int]]:
    return {c for _, c in img.convert("RGB").getcolors(maxcolors=2_000_000)}


def make_idea(date: str = "2026-11-23", hook: str = HOOK) -> Idea:
    return Idea(date=date, status="ready", topic="Stoicism", hook=hook, caption="A caption. #stoicism")


def test_post_is_1080x1350():
    assert render_image(HOOK, "Stoicism", seed=1).size == (1080, 1350)


def test_only_black_white_and_grey():
    found = tones(render_image(HOOK, "Stoicism", seed=1))
    assert all(r == g == b for r, g, b in found)
    assert (255, 255, 255) in found


def test_post_is_dark_picture_not_flat_black():
    img = render_image(HOOK, "Stoicism", seed=1)
    assert ImageStat.Stat(img.convert("L")).mean[0] < 80
    assert len(tones(img)) >= 60


def test_long_text_never_enters_the_side_margins():
    img = render_image("word " * 40, "Stoicism", seed=1).convert("L")
    assert img.crop((0, 0, 60, 1350)).getextrema()[1] < TEXT_WHITE
    assert img.crop((1020, 0, 1080, 1350)).getextrema()[1] < TEXT_WHITE


def test_same_inputs_give_the_same_image():
    a = render_image(HOOK, "Stoicism", seed=4)
    b = render_image(HOOK, "Stoicism", seed=4)
    assert ImageChops.difference(a, b).getbbox() is None


def test_seed_changes_the_picture():
    a = render_image(HOOK, "Stoicism", seed=4)
    b = render_image(HOOK, "Stoicism", seed=5)
    assert ImageChops.difference(a, b).getbbox() is not None


def test_hook_lines_are_balanced_with_no_lone_last_word():
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    _, lines, _ = fit_hook("You test your own ideas the wrong way", 500, draw)
    assert len(lines) == 2
    assert all(len(line.split()) >= 3 for line in lines)


def test_curly_quotes_accents_dashes_render():
    text = "Nietzsche’s “abyss” — café, naïve"
    render_image(text, text, seed=1)


def test_missing_glyph_in_hook_raises():
    with pytest.raises(UnsupportedGlyphError):
        render_image("漢字", "Stoicism", seed=1)


def test_missing_glyph_in_topic_raises():
    with pytest.raises(UnsupportedGlyphError):
        render_image(HOOK, "漢字", seed=1)


def test_text_too_long_for_the_post_raises():
    with pytest.raises(TextOverflowError):
        render_image("word " * 2000, "Stoicism", seed=1)


def test_render_post_writes_one_png(tmp_path: Path):
    paths = render_post(make_idea(), tmp_path / "2026-11-23")
    assert paths == [tmp_path / "2026-11-23" / "post.png"]
    assert Image.open(paths[0]).size == (1080, 1350)


def test_each_day_gets_its_own_picture_and_a_rerun_matches(tmp_path: Path):
    (a,) = render_post(make_idea("2026-11-23"), tmp_path / "a")
    (again,) = render_post(make_idea("2026-11-23"), tmp_path / "again")
    (b,) = render_post(make_idea("2026-11-24"), tmp_path / "b")
    assert a.read_bytes() == again.read_bytes()
    assert a.read_bytes() != b.read_bytes()
