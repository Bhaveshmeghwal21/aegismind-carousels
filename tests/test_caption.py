from carousel.caption import build_caption, display_quote
from carousel.library import load_library
from carousel.models import Idea
from carousel.music import load_music

QUOTE = "Think lightly of yourself and deeply of the world."


def idea(**changes) -> Idea:
    fields = dict(
        date="2026-11-23",
        status="ready",
        quote=QUOTE,
        author="Miyamoto Musashi",
        source="Dokkōdō (1645)",
        caption="A line of reflection.",
        tags="#musashi #stoic",
    )
    fields.update(changes)
    return Idea(**fields)


def test_display_quote_adds_curly_quotes_once():
    assert display_quote("Be here.") == "“Be here.”"
    assert display_quote("“Be here.”") == "“Be here.”"
    assert display_quote('"Be here."') == "“Be here.”"


def test_caption_has_quote_attribution_reflection_art_credit_and_tags_in_order(art_dir):
    piece = load_library(art_dir)["a1"]
    assert build_caption(idea(), piece) == (
        "“Think lightly of yourself and deeply of the world.”\n"
        "— Miyamoto Musashi, Dokkōdō (1645)\n"
        "\n"
        "A line of reflection.\n"
        "\n"
        "Art: Piece a1, Unknown, c. 100 CE. The Cleveland Museum of Art, open access (CC0)\n"
        "\n"
        "#musashi #stoic"
    )


def test_caption_credits_the_music_right_after_the_art(art_dir, music_dir):
    piece = load_library(art_dir)["a1"]
    track = load_music(music_dir)["tone-a"]
    text = build_caption(idea(), piece, track)
    assert (
        "Art: Piece a1, Unknown, c. 100 CE. The Cleveland Museum of Art, open access (CC0)\n"
        "Music: Tone A, Test Composer, performed by Test Player, 1916. Public domain\n"
        "\n"
        "#musashi #stoic"
    ) in text


def test_caption_skips_the_parts_an_entry_leaves_out(art_dir):
    piece = load_library(art_dir)["a1"]
    text = build_caption(idea(source="", caption="", tags=""), piece)
    assert text == (
        "“Think lightly of yourself and deeply of the world.”\n"
        "— Miyamoto Musashi\n"
        "\n"
        "Art: Piece a1, Unknown, c. 100 CE. The Cleveland Museum of Art, open access (CC0)"
    )
