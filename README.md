# aegismind-carousels

Content and tooling for the Instagram account @theaegismind: dark, moody single-image posts about philosophy and psychology (black, white and grey only, in a serif font). The repo name says carousels because that was the first plan; for now every post is one picture.

## How it works

- `ideas/YYYY-Www.md`: one file per week, one entry per day. A weekly Claude routine drafts the next week; you edit or add entries on GitHub.
- `src/carousel/`: the image-maker. `python -m carousel render --date YYYY-MM-DD` turns that day's entry into `posts/YYYY-MM-DD/post.png` (1080x1350). The dark landscape behind the text is drawn by code and differs every day.
- A daily Claude routine renders the day's image, pushes it here (the repo is public so Instagram can fetch the image) and schedules the post through Metricool.
- `routines/weekly.md` and `routines/daily.md`: the instructions each routine follows. Edit these to change how a routine behaves.
- `config.json`: Metricool brand id, post time, and `publish_mode`.

## Editing an ideas entry

```
## 2026-11-23
status: ready              # ready, or needs-check (never posted)
topic: Stoicism            # small label above the line, at most 25 characters
hook: Marcus Aurelius rehearsed bad days every morning    # the line on the image, at most 50 characters
caption: Three to five short sentences. One thing to try. #hashtag #hashtag
```

The image carries only the topic and the hook. Everything else goes in the caption. An optional `slides:` block (`- Title :: body` lines) is accepted and ignored for now, in case carousels come back.

## Going live

`publish_mode` in `config.json` starts as `draft`: posts are created as drafts in Metricool for you to review. Change it to `auto` once you are happy.

## Local setup

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest
```

The font is EB Garamond (SIL Open Font License 1.1), in `assets/fonts/`.
