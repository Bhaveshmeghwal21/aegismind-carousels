from pathlib import Path

import pytest

from carousel.errors import IdeaParseError
from carousel.ideas import idea_for_date, is_postable, load_ideas, parse_ideas
from carousel.models import Slide
from carousel.render import render_post

REPO = Path(__file__).resolve().parents[1]

VALID = """\
## 2026-11-23
status: ready
topic: Stoicism
hook: Seneca rehearsed disaster every morning
slides:
- Premeditatio malorum :: Imagine the worst before it comes.
- Loss is borrowed :: Everything you love was lent to you.
- Fear is a forecast :: Most of what we dread never happens.
- Rehearse, then relax :: Face it in thought first.
- Your move :: Name one fear tonight.
caption: Short caption. #stoicism #philosophy
"""

SECOND = VALID.replace("2026-11-23", "2026-11-24").replace("Stoicism", "Psychology")


def test_parses_valid_entry():
    (idea,) = parse_ideas(VALID)
    assert idea.date == "2026-11-23"
    assert idea.status == "ready"
    assert idea.topic == "Stoicism"
    assert idea.hook == "Seneca rehearsed disaster every morning"
    assert len(idea.slides) == 5
    assert idea.slides[0] == Slide("Premeditatio malorum", "Imagine the worst before it comes.")
    assert idea.caption == "Short caption. #stoicism #philosophy"


def test_two_entries_parse_in_order():
    ideas = parse_ideas(VALID + "\n" + SECOND)
    assert [i.date for i in ideas] == ["2026-11-23", "2026-11-24"]
    assert ideas[1].topic == "Psychology"


def test_missing_hook_raises_with_date():
    text = VALID.replace("hook: Seneca rehearsed disaster every morning\n", "")
    with pytest.raises(IdeaParseError, match="2026-11-23"):
        parse_ideas(text)


def test_slide_line_without_separator_raises_with_date():
    text = VALID.replace("Loss is borrowed :: ", "Loss is borrowed ")
    with pytest.raises(IdeaParseError, match="2026-11-23"):
        parse_ideas(text)


def test_unknown_status_raises_with_date():
    with pytest.raises(IdeaParseError, match="2026-11-23"):
        parse_ideas(VALID.replace("status: ready", "status: maybe"))


def test_one_bad_entry_does_not_hide_which_one():
    text = VALID + "\n" + SECOND.replace("topic: Psychology\n", "")
    with pytest.raises(IdeaParseError, match="2026-11-24"):
        parse_ideas(text)


def test_only_date_ignores_malformed_entries_for_other_dates():
    text = VALID + "\n" + SECOND.replace("topic: Psychology\n", "")
    (idea,) = parse_ideas(text, only_date="2026-11-23")
    assert idea.date == "2026-11-23"


def test_idea_for_date_returns_none_when_absent():
    ideas = parse_ideas(VALID)
    assert idea_for_date(ideas, "2026-11-30") is None
    assert idea_for_date(ideas, "2026-11-23") == ideas[0]


def test_needs_check_is_not_postable():
    (idea,) = parse_ideas(VALID.replace("status: ready", "status: needs-check"))
    assert not is_postable(idea)


NO_SLIDES = """\
## 2026-11-23
status: ready
topic: Stoicism
hook: Seneca rehearsed disaster every morning
caption: Short caption. #stoicism #philosophy
"""


def test_entry_without_slides_is_valid_and_postable():
    (idea,) = parse_ideas(NO_SLIDES)
    assert idea.slides == []
    assert is_postable(idea)


def test_ready_entry_with_slides_is_postable():
    (idea,) = parse_ideas(VALID)
    assert is_postable(idea)


def test_load_ideas_reads_all_files_sorted_by_date(tmp_path):
    (tmp_path / "2026-W48.md").write_text(SECOND, encoding="utf-8")
    (tmp_path / "2026-W47.md").write_text(VALID, encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
    assert [i.date for i in load_ideas(tmp_path)] == ["2026-11-23", "2026-11-24"]


def test_first_week_file_is_valid_and_renders(tmp_path):
    ideas = parse_ideas((REPO / "ideas" / "2026-W48.md").read_text(encoding="utf-8"))
    assert [i.date for i in ideas] == [f"2026-11-{d}" for d in range(23, 30)]
    for idea in ideas:
        assert is_postable(idea), idea.date
        render_post(idea, tmp_path / idea.date)
