# aegismind-carousels

Content and tooling for the Instagram account @theaegismind: dark, moody single-image posts. Each post is a quote by a real thinker (Marcus Aurelius, Seneca, Buddha, Musashi, Osho, Socrates and so on) in white serif type over black-and-white art, with the thinker's name under it. The repo name says carousels because that was the first plan; for now every post is one picture.

## How it works

- `ideas/YYYY-Www.md`: one file per week, one entry per day. A weekly Claude routine drafts the next week; you edit or add entries on GitHub.
- `assets/art/`: the art library. Public-domain pictures (Cleveland Museum of Art open access, CC0) with `index.json` saying how to frame and darken each one. Each post uses the entry's `image:` id, or one picked by date.
- `src/carousel/`: the image-maker. `python -m carousel render --date YYYY-MM-DD` writes `posts/YYYY-MM-DD/post.png` (1080x1350) and `posts/YYYY-MM-DD/caption.txt` (quote, source, reflection, art credit, hashtags).
- A daily Claude routine renders the day's post, pushes it here (the repo is public so Instagram can fetch the image) and schedules it through Metricool.
- `routines/weekly.md` and `routines/daily.md`: the instructions each routine follows. Edit these to change how a routine behaves.
- `config.json`: Metricool brand id, post time, and `publish_mode`.

## Editing an ideas entry

```
## 2026-11-23
status: ready              # ready, or needs-check (never posted)
quote: We suffer more often in imagination than in reality.     # the words, without quotation marks
author: Seneca             # shown under the quote
source: Letters to Lucilius 13, tr. Richard Gummere             # work and translator, goes in the caption
image: 108313              # optional: an id from assets/art/index.json
caption: Most of what we dread never arrives.                   # optional reflection
tags: #seneca #stoicism #philosophy                             # optional
note: anything you want to remember   # optional, ignored
```

Only `status`, `quote` and `author` are required. Use a quote you can trace to a real work; misattributed quotes are everywhere. Quotes up to about 140 characters fit the image.

## Going live

`publish_mode` in `config.json` starts as `draft`: posts are created as drafts in Metricool for you to review. Change it to `auto` once you are happy.

## Local setup

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest
```

The font is EB Garamond (SIL Open Font License 1.1), in `assets/fonts/`. Artwork credits are in `assets/art/index.json` and in every caption.
