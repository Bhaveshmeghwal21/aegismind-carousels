import json
from pathlib import Path

from carousel.cli import already_posted, main, mark_posted

ENTRY = """\
## {date}
status: {status}
quote: Think lightly of yourself and deeply of the world.
author: Miyamoto Musashi
source: Dokkōdō (1645)
image: a1
caption: A line of reflection.
tags: #musashi
"""


def entry(date="2026-11-23", status="ready", drop_quote=False):
    text = ENTRY.format(date=date, status=status)
    if drop_quote:
        text = "\n".join(line for line in text.splitlines() if not line.startswith("quote:")) + "\n"
    return text


def setup(tmp_path: Path, art_dir: Path, *entries: str, approved: bool = True) -> dict[str, Path]:
    ideas = tmp_path / "ideas"
    ideas.mkdir()
    header = "approved: yes\n\n" if approved else ""
    (ideas / "2026-W48.md").write_text(header + "\n".join(entries), encoding="utf-8")
    return {"ideas": ideas, "posts": tmp_path / "posts", "art": art_dir}


def render(p: dict[str, Path], date: str) -> int:
    return main(["render", "--date", date, "--ideas", str(p["ideas"]), "--out", str(p["posts"]), "--art", str(p["art"])])


def test_render_prints_the_post_path_writes_the_caption_and_exits_0(tmp_path, art_dir, capsys):
    p = setup(tmp_path, art_dir, entry())
    assert render(p, "2026-11-23") == 0
    paths = json.loads(capsys.readouterr().out)
    assert [Path(x).name for x in paths] == ["post.png"]
    assert all(Path(x).exists() for x in paths)
    caption = (p["posts"] / "2026-11-23" / "caption.txt").read_text(encoding="utf-8")
    assert "— Miyamoto Musashi, Dokkōdō (1645)" in caption


def test_no_entry_for_date_exits_3_and_writes_nothing(tmp_path, art_dir):
    p = setup(tmp_path, art_dir, entry())
    assert render(p, "2026-11-30") == 3
    assert not (p["posts"] / "2026-11-30").exists()


def test_needs_check_entry_exits_3_and_writes_nothing(tmp_path, art_dir):
    p = setup(tmp_path, art_dir, entry(status="needs-check"))
    assert render(p, "2026-11-23") == 3
    assert not (p["posts"] / "2026-11-23").exists()


def test_unapproved_week_exits_3_says_so_and_writes_nothing(tmp_path, art_dir, capsys):
    p = setup(tmp_path, art_dir, entry(), approved=False)
    assert render(p, "2026-11-23") == 3
    err = capsys.readouterr().err
    assert "2026-11-23" in err and "not approved" in err
    assert not (p["posts"] / "2026-11-23").exists()


def test_malformed_entry_for_the_date_exits_3_and_names_the_date(tmp_path, art_dir, capsys):
    p = setup(tmp_path, art_dir, entry(drop_quote=True))
    assert render(p, "2026-11-23") == 3
    assert "2026-11-23" in capsys.readouterr().err


def test_unknown_image_id_exits_3_and_writes_nothing(tmp_path, art_dir, capsys):
    p = setup(tmp_path, art_dir, entry().replace("image: a1", "image: nope"))
    assert render(p, "2026-11-23") == 3
    assert "nope" in capsys.readouterr().err
    assert not (p["posts"] / "2026-11-23").exists()


def test_malformed_entry_for_another_day_does_not_block_today(tmp_path, art_dir):
    p = setup(tmp_path, art_dir, entry("2026-11-23"), entry("2026-11-24", drop_quote=True))
    assert render(p, "2026-11-23") == 0


def test_already_posted_exits_4_and_renders_nothing(tmp_path, art_dir):
    p = setup(tmp_path, art_dir, entry())
    assert render(p, "2026-11-23") == 0
    (p["posts"] / "2026-11-23" / "post.png").unlink()
    mark_posted(p["posts"], "2026-11-23", "draft", "https://example.test/post/1")
    assert render(p, "2026-11-23") == 4
    assert not (p["posts"] / "2026-11-23" / "post.png").exists()


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
