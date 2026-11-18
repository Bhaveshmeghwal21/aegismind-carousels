import pytest
from PIL import Image

from carousel.errors import TextOverflowError, UnsupportedGlyphError
from carousel.models import Idea, Slide
from carousel.render import render_carousel, render_slide

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (230, 0, 0)


def colours(img: Image.Image) -> set[tuple[int, int, int]]:
    return {c for _, c in img.convert("RGB").getcolors(maxcolors=1_500_000)}


def make_idea(n_slides: int = 5) -> Idea:
    return Idea(
        date="2026-11-23",
        status="ready",
        topic="Stoicism",
        hook="Seneca rehearsed disaster every morning",
        slides=[Slide(title=f"Idea {i}", body="Imagine the worst before it comes.") for i in range(n_slides)],
        caption="A short caption. #stoicism",
    )


def test_slide_is_1080x1350():
    img = render_slide("hook", "Why Stoics expected the worst", "", 1, 7)
    assert img.size == (1080, 1350)


def test_only_black_white_red_family():
    img = render_slide(
        "idea", "Premeditatio malorum", "Imagine the worst before it comes, so it cannot ambush you.", 2, 7
    )
    found = colours(img)
    assert all(g == b and r >= g for r, g, b in found)
    assert RED in found
    assert WHITE in found


def test_long_text_never_overflows_margins():
    img = render_slide("idea", "A long title that keeps going and going", "word " * 80, 2, 7).convert("RGB")
    left = img.crop((0, 0, 60, 1350))
    right = img.crop((1020, 0, 1080, 1350))
    assert colours(left) == {BLACK}
    assert colours(right) == {BLACK}


def test_curly_quotes_accents_dashes_render():
    text = "Nietzsche’s “abyss” — café, naïve"
    render_slide("idea", text, text, 2, 7)


def test_missing_glyph_raises():
    with pytest.raises(UnsupportedGlyphError):
        render_slide("idea", "漢字", "", 2, 7)


def test_text_too_long_for_slide_raises():
    with pytest.raises(TextOverflowError):
        render_slide("idea", "Title", "word " * 2000, 2, 7)


def test_carousel_slide_count(tmp_path):
    paths = render_carousel(make_idea(5), tmp_path, "Follow for more.")
    assert [p.name for p in paths] == [f"slide-{i}.png" for i in range(1, 8)]
    for p in paths:
        assert p.exists()
        assert Image.open(p).size == (1080, 1350)
