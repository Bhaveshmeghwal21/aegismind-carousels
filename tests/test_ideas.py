from pathlib import Path

import pytest

from carousel.errors import IdeaParseError
from carousel.ideas import idea_for_date, is_postable, load_ideas, parse_ideas
from carousel.library import load_library, pick_art
from carousel.render import render_post
from conftest import REAL_ART_DIR, REPO

APPROVED = "approved: yes\n\n"

VALID = APPROVED + """\
## 2026-11-23
status: ready
quote: Such as are thy habitual thoughts, such also will be the character of thy mind; for the soul is dyed by the thoughts.
author: Marcus Aurelius
source: Meditations 5.16, tr. George Long
image: 108313
caption: What do you let your mind rehearse all day?
tags: #stoicism #marcusaurelius
"""

MINIMAL = """\
## 2026-11-24
status: ready
quote: Think lightly of yourself and deeply of the world.
author: Miyamoto Musashi
"""


def test_parses_a_full_entry():
    (idea,) = parse_ideas(VALID)
    assert idea.date == "2026-11-23"
    assert idea.status == "ready"
    assert idea.quote.startswith("Such as are thy habitual thoughts")
    assert idea.author == "Marcus Aurelius"
    assert idea.source == "Meditations 5.16, tr. George Long"
    assert idea.image == "108313"
    assert idea.caption == "What do you let your mind rehearse all day?"
    assert idea.tags == "#stoicism #marcusaurelius"


def test_a_minimal_entry_needs_only_status_quote_and_author():
    (idea,) = parse_ideas(MINIMAL)
    assert (idea.source, idea.image, idea.caption, idea.tags) == ("", "", "", "")


def test_two_entries_parse_in_order():
    ideas = parse_ideas(VALID + "\n" + MINIMAL)
    assert [i.date for i in ideas] == ["2026-11-23", "2026-11-24"]
    assert ideas[1].author == "Miyamoto Musashi"


def test_a_colon_inside_the_quote_is_kept():
    (idea,) = parse_ideas(MINIMAL.replace("Think lightly", "Note: think lightly"))
    assert idea.quote.startswith("Note: think lightly")


@pytest.mark.parametrize("missing", ["quote", "author", "status"])
def test_missing_required_field_raises_with_the_date(missing):
    lines = [line for line in VALID.splitlines() if not line.startswith(f"{missing}:")]
    with pytest.raises(IdeaParseError, match="2026-11-23"):
        parse_ideas("\n".join(lines))


def test_line_without_a_colon_raises_with_date():
    with pytest.raises(IdeaParseError, match="2026-11-23"):
        parse_ideas(VALID + "stray words\n")


def test_unknown_status_raises_with_date():
    with pytest.raises(IdeaParseError, match="2026-11-23"):
        parse_ideas(VALID.replace("status: ready", "status: maybe"))


def test_one_bad_entry_does_not_hide_which_one():
    text = VALID + "\n" + MINIMAL.replace("author: Miyamoto Musashi\n", "")
    with pytest.raises(IdeaParseError, match="2026-11-24"):
        parse_ideas(text)


def test_only_date_ignores_malformed_entries_for_other_dates():
    text = VALID + "\n" + MINIMAL.replace("author: Miyamoto Musashi\n", "")
    (idea,) = parse_ideas(text, only_date="2026-11-23")
    assert idea.date == "2026-11-23"


def test_idea_for_date_returns_none_when_absent():
    ideas = parse_ideas(VALID)
    assert idea_for_date(ideas, "2026-11-30") is None
    assert idea_for_date(ideas, "2026-11-23") == ideas[0]


def test_needs_check_is_not_postable():
    (idea,) = parse_ideas(VALID.replace("status: ready", "status: needs-check"))
    assert not is_postable(idea)


def test_ready_entry_in_an_approved_week_is_postable():
    (idea,) = parse_ideas(APPROVED + MINIMAL)
    assert idea.status == "ready"
    assert is_postable(idea)


def test_a_week_without_an_approval_line_is_not_postable():
    (idea,) = parse_ideas(MINIMAL)
    assert idea.status == "proposed"
    assert not is_postable(idea)


@pytest.mark.parametrize("header", ["approved: no\n\n", "approved:\n\n", "approved: maybe\n\n"])
def test_a_week_not_approved_yes_is_not_postable(header):
    (idea,) = parse_ideas(header + MINIMAL)
    assert idea.status == "proposed" and not is_postable(idea)


def test_approval_line_is_case_insensitive_and_one_line_approves_every_entry():
    ideas = parse_ideas("Approved: YES\n\n" + MINIMAL + "\n" + MINIMAL.replace("11-24", "11-25"))
    assert [i.status for i in ideas] == ["ready", "ready"]


def test_approval_never_overrides_needs_check():
    (idea,) = parse_ideas(APPROVED + MINIMAL.replace("status: ready", "status: needs-check"))
    assert idea.status == "needs-check" and not is_postable(idea)


def test_load_ideas_reads_all_files_sorted_by_date(tmp_path):
    (tmp_path / "2026-W48.md").write_text(MINIMAL, encoding="utf-8")
    (tmp_path / "2026-W47.md").write_text(VALID, encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
    assert [i.date for i in load_ideas(tmp_path)] == ["2026-11-23", "2026-11-24"]


def test_first_week_file_is_valid_and_renders(tmp_path):
    text = (REPO / "ideas" / "2026-W48.md").read_text(encoding="utf-8")
    ideas = parse_ideas(text.replace("approved: no", "approved: yes"))  # once approved, every entry must post
    assert [i.date for i in ideas] == [f"2026-11-{d}" for d in range(23, 30)]
    library = load_library(REAL_ART_DIR)
    for idea in ideas:
        assert is_postable(idea), idea.date
        assert idea.source, f"{idea.date}: every quote needs a source"
        pick_art(library, idea.date, idea.image or None)
        render_post(idea, tmp_path / idea.date, REAL_ART_DIR)
