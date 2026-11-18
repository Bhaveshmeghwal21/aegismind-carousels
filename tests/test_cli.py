import json
from pathlib import Path

from carousel.cli import already_posted, main, mark_posted

ENTRY = """\
## {date}
status: {status}
topic: Stoicism
{hook_line}hook: Marcus rehearsed bad days every morning
slides:
- Meditations 2.1 :: Marcus expected the meddler and the ungrateful.
- Why do that? :: Expecting friction removes the shock.
- Imagination vs reality :: We suffer more often in imagination than in reality.
- The point :: Not pessimism. Preparation.
- Your move :: Name one difficult moment ahead.
caption: Prepare for the day. #stoicism
"""


def entry(date="2026-11-23", status="ready", drop_hook=False):
    text = ENTRY.format(date=date, status=status, hook_line="")
    if drop_hook:
        text = text.replace("hook: Marcus rehearsed bad days every morning\n", "")
    return text


def setup(tmp_path: Path, *entries: str) -> dict[str, Path]:
    ideas = tmp_path / "ideas"
    ideas.mkdir()
    (ideas / "2026-W48.md").write_text("\n".join(entries), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"closing_line": "Follow for more."}), encoding="utf-8")
    return {"ideas": ideas, "posts": tmp_path / "posts", "config": config}


def render(p: dict[str, Path], date: str) -> int:
    return main(
        ["render", "--date", date, "--ideas", str(p["ideas"]), "--out", str(p["posts"]), "--config", str(p["config"])]
    )


def test_render_prints_slide_paths_and_exits_0(tmp_path, capsys):
    p = setup(tmp_path, entry())
    assert render(p, "2026-11-23") == 0
    paths = json.loads(capsys.readouterr().out)
    assert [Path(x).name for x in paths] == [f"slide-{i}.png" for i in range(1, 8)]
    assert all(Path(x).exists() for x in paths)


def test_no_entry_for_date_exits_3_and_writes_nothing(tmp_path):
    p = setup(tmp_path, entry())
    assert render(p, "2026-11-30") == 3
    assert not (p["posts"] / "2026-11-30").exists()


def test_needs_check_entry_exits_3_and_writes_nothing(tmp_path):
    p = setup(tmp_path, entry(status="needs-check"))
    assert render(p, "2026-11-23") == 3
    assert not (p["posts"] / "2026-11-23").exists()


def test_malformed_entry_for_the_date_exits_3_and_names_the_date(tmp_path, capsys):
    p = setup(tmp_path, entry(drop_hook=True))
    assert render(p, "2026-11-23") == 3
    assert "2026-11-23" in capsys.readouterr().err


def test_malformed_entry_for_another_day_does_not_block_today(tmp_path):
    p = setup(tmp_path, entry("2026-11-23"), entry("2026-11-24", drop_hook=True))
    assert render(p, "2026-11-23") == 0


def test_already_posted_exits_4_and_renders_nothing(tmp_path):
    p = setup(tmp_path, entry())
    assert render(p, "2026-11-23") == 0
    (p["posts"] / "2026-11-23" / "slide-1.png").unlink()
    mark_posted(p["posts"], "2026-11-23", "draft", "https://example.test/post/1")
    assert render(p, "2026-11-23") == 4
    assert not (p["posts"] / "2026-11-23" / "slide-1.png").exists()


def test_mark_posted_writes_marker_that_already_posted_sees(tmp_path):
    posts = tmp_path / "posts"
    assert not already_posted(posts, "2026-11-23")
    path = mark_posted(posts, "2026-11-23", "draft", "https://example.test/post/1")
    assert already_posted(posts, "2026-11-23")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["mode"] == "draft"
    assert data["planner_url"] == "https://example.test/post/1"


def test_mark_posted_command_writes_marker(tmp_path):
    posts = tmp_path / "posts"
    code = main(
        ["mark-posted", "--date", "2026-11-23", "--posts", str(posts), "--mode", "auto", "--url", "https://example.test/x"]
    )
    assert code == 0
    assert already_posted(posts, "2026-11-23")
