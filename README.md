# aegismind-carousels

Content and tooling for the Instagram account @theaegismind: dark, bold carousels about philosophy and psychology (black, white and red only).

## How it works

- `ideas/YYYY-Www.md`: one file per week, one entry per day. A weekly Claude routine drafts the next week; you edit or add entries on GitHub.
- `src/carousel/`: the slide-maker. `python -m carousel render --date YYYY-MM-DD` turns that day's entry into `posts/YYYY-MM-DD/slide-N.png` (1080x1350).
- A daily Claude routine renders the day's slides, pushes them here (the repo is public so Instagram can fetch the images) and schedules the post through Metricool.
- `routines/weekly.md` and `routines/daily.md`: the instructions each routine follows. Edit these to change how a routine behaves.
- `config.json`: Metricool brand id, post time, and `publish_mode`.

## Editing an ideas entry

```
## 2026-11-23
status: ready              # ready, or needs-check (never posted)
topic: Stoicism
hook: Marcus Aurelius rehearsed bad days every morning
slides:
- Short title :: One or two short sentences.
- ... (4 to 6 slides in total)
caption: One short caption. #hashtag #hashtag
```

Keep the hook under about 50 characters, titles under 25 and bodies under 140.

## Going live

`publish_mode` in `config.json` starts as `draft`: posts are created as drafts in Metricool for you to review. Change it to `auto` once you are happy.

## Local setup

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest
```
