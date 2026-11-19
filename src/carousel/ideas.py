import re
from pathlib import Path

from .errors import IdeaParseError
from .models import Idea

STATUSES = ("ready", "needs-check")
REQUIRED_FIELDS = ("status", "quote", "author")
HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def _week_is_approved(preamble: str) -> bool:
    """True only when the lines above the first entry say 'approved: yes'. Anything else, or no line, is not approved."""
    for raw in preamble.splitlines():
        key, sep, value = raw.partition(":")
        if sep and key.strip().lower() == "approved":
            return value.strip().lower() == "yes"
    return False


def _parse_entry(date: str, block: str, approved: bool) -> Idea:
    fields: dict[str, str] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise IdeaParseError(f"{date}: cannot read line {line!r}")
        fields[key.strip().lower()] = value.strip()
    for name in REQUIRED_FIELDS:
        if not fields.get(name):
            raise IdeaParseError(f"{date}: missing '{name}'")
    if fields["status"].lower() not in STATUSES:
        raise IdeaParseError(f"{date}: status must be one of {STATUSES}, got {fields['status']!r}")
    status = fields["status"].lower()
    if status == "ready" and not approved:
        status = "proposed"  # written by the routine, waiting for the owner's 'approved: yes'
    return Idea(
        date=date,
        status=status,
        quote=fields["quote"],
        author=fields["author"],
        source=fields.get("source", ""),
        image=fields.get("image", ""),
        caption=fields.get("caption", ""),
        tags=fields.get("tags", ""),
        music=fields.get("music", ""),
    )


def parse_ideas(text: str, only_date: str | None = None) -> list[Idea]:
    """Parse '## YYYY-MM-DD' entries. With only_date, other entries are not parsed (a typo in
    one day's entry must not block another day's post). Unknown keys such as 'note:' are ignored.
    Entries marked ready only count as ready if the file starts with 'approved: yes'."""
    matches = list(HEADING.finditer(text))
    approved = _week_is_approved(text[: matches[0].start()]) if matches else False
    ideas = []
    for i, match in enumerate(matches):
        date = match.group(1)
        if only_date is not None and date != only_date:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ideas.append(_parse_entry(date, text[match.end() : end], approved))
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
