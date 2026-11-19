import re
from pathlib import Path

from .errors import IdeaParseError
from .models import Idea, Slide

STATUSES = ("ready", "needs-check")
REQUIRED_FIELDS = ("status", "topic", "hook", "caption")
HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def _parse_entry(date: str, block: str) -> Idea:
    fields: dict[str, str] = {}
    slides: list[Slide] = []
    in_slides = False
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if in_slides and line.startswith("- "):
            title, sep, body = line[2:].partition(" :: ")
            if not sep or not title.strip() or not body.strip():
                raise IdeaParseError(f"{date}: slide line needs 'Title :: body', got {line!r}")
            slides.append(Slide(title.strip(), body.strip()))
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise IdeaParseError(f"{date}: cannot read line {line!r}")
        key = key.strip().lower()
        in_slides = key == "slides"
        if not in_slides:
            fields[key] = value.strip()
    for name in REQUIRED_FIELDS:
        if not fields.get(name):
            raise IdeaParseError(f"{date}: missing '{name}'")
    if fields["status"].lower() not in STATUSES:
        raise IdeaParseError(f"{date}: status must be one of {STATUSES}, got {fields['status']!r}")
    return Idea(
        date=date,
        status=fields["status"].lower(),
        topic=fields["topic"],
        hook=fields["hook"],
        caption=fields["caption"],
        slides=slides,
    )


def parse_ideas(text: str, only_date: str | None = None) -> list[Idea]:
    """Parse '## YYYY-MM-DD' entries. With only_date, other entries are not parsed (a typo in
    one day's entry must not block another day's post)."""
    matches = list(HEADING.finditer(text))
    ideas = []
    for i, match in enumerate(matches):
        date = match.group(1)
        if only_date is not None and date != only_date:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ideas.append(_parse_entry(date, text[match.end() : end]))
    return ideas


def load_ideas(ideas_dir: Path, only_date: str | None = None) -> list[Idea]:
    ideas: list[Idea] = []
    for path in sorted(Path(ideas_dir).glob("*.md")):
        try:
            ideas.extend(parse_ideas(path.read_text(encoding="utf-8"), only_date))
        except IdeaParseError as err:
            raise IdeaParseError(f"{path.name}: {err}") from err
    return sorted(ideas, key=lambda idea: idea.date)


def idea_for_date(ideas: list[Idea], date: str) -> Idea | None:
    return next((idea for idea in ideas if idea.date == date), None)


def is_postable(idea: Idea) -> bool:
    return idea.status == "ready"
