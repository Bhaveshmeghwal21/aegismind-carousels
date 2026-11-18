import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .errors import IdeaParseError
from .ideas import idea_for_date, is_postable, load_ideas
from .render import render_carousel

EXIT_OK = 0
EXIT_NOTHING_TO_POST = 3
EXIT_ALREADY_POSTED = 4
DEFAULT_CLOSING_LINE = "Follow for more."


def already_posted(posts_dir: Path, date: str) -> bool:
    return (Path(posts_dir) / date / "posted.json").exists()


def mark_posted(posts_dir: Path, date: str, mode: str, planner_url: str) -> Path:
    path = Path(posts_dir) / date / "posted.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "date": date,
        "mode": mode,
        "planner_url": planner_url,
        "marked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def _closing_line(config_path: Path) -> str:
    if not config_path.exists():
        return DEFAULT_CLOSING_LINE
    return json.loads(config_path.read_text(encoding="utf-8")).get("closing_line", DEFAULT_CLOSING_LINE)


def _render(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    if already_posted(out_dir, args.date):
        print(f"{args.date}: already posted, nothing rendered", file=sys.stderr)
        return EXIT_ALREADY_POSTED
    try:
        ideas = load_ideas(Path(args.ideas), only_date=args.date)
    except IdeaParseError as err:
        print(f"{args.date}: ideas entry is malformed: {err}", file=sys.stderr)
        return EXIT_NOTHING_TO_POST
    idea = idea_for_date(ideas, args.date)
    if idea is None:
        print(f"{args.date}: no idea found for this date", file=sys.stderr)
        return EXIT_NOTHING_TO_POST
    if not is_postable(idea):
        print(f"{args.date}: idea is not postable (status {idea.status!r}, {len(idea.slides)} slides)", file=sys.stderr)
        return EXIT_NOTHING_TO_POST
    paths = render_carousel(idea, out_dir / args.date, _closing_line(Path(args.config)))
    print(json.dumps([p.as_posix() for p in paths]))
    return EXIT_OK


def _mark_posted(args: argparse.Namespace) -> int:
    print(mark_posted(Path(args.posts), args.date, args.mode, args.url).as_posix())
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="carousel")
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render", help="render the carousel for a date")
    render.add_argument("--date", required=True, help="YYYY-MM-DD")
    render.add_argument("--ideas", default="ideas")
    render.add_argument("--out", default="posts")
    render.add_argument("--config", default="config.json")
    render.set_defaults(func=_render)

    mark = sub.add_parser("mark-posted", help="record that a date has been posted or drafted")
    mark.add_argument("--date", required=True, help="YYYY-MM-DD")
    mark.add_argument("--posts", default="posts")
    mark.add_argument("--mode", required=True, choices=["draft", "auto"])
    mark.add_argument("--url", required=True)
    mark.set_defaults(func=_mark_posted)

    args = parser.parse_args(argv)
    return args.func(args)
