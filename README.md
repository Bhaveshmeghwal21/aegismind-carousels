# aegismind-carousels

Content and tooling for the Instagram account @theaegismind: dark, moody single-image posts. Each post is a quote by a real thinker (Marcus Aurelius, Seneca, Buddha, Musashi, Osho, Socrates and so on) in white serif type over black-and-white art, with the thinker's name under it. The repo name says carousels because that was the first plan; for now every post is one picture.

## How it works

- `ideas/YYYY-Www.md`: one file per week, one entry per day. A weekly Claude routine drafts the next week; you edit or add entries on GitHub.
- `assets/art/`: the art library. Public-domain pictures (Cleveland Museum of Art open access, CC0) with `index.json` saying how to frame and darken each one. Each post uses the entry's `image:` id, or one picked by date.
- `assets/music/`: the music library. Short clips of public-domain recordings (Bach played by Kimiko Ishizaka under CC0, a Chopin nocturne from 1916, Beethoven's "Moonlight" from 1922, and others) with `index.json` giving each one's licence, source and mood. Each post uses the entry's `music:` id, or one picked by date.
- `src/carousel/`: the post-maker. `python -m carousel render --date YYYY-MM-DD --reel 10` writes `posts/YYYY-MM-DD/post.png` (1080x1350), `posts/YYYY-MM-DD/reel.mp4` (the same image held still for 10 seconds on a 1080x1920 frame, with the music mixed in) and `posts/YYYY-MM-DD/caption.txt` (quote, source, reflection, art and music credits, hashtags). Instagram only attaches music to Reels, so the music is baked into the video instead of using Instagram's library, which this account cannot reach.
- A daily Claude routine renders the day's Reel, pushes it here (the repo is public so Instagram can fetch the video) and schedules it through Metricool.
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
music: goldberg-var25      # optional: an id from assets/music/index.json
caption: Most of what we dread never arrives.                   # optional reflection
tags: #seneca #stoicism #philosophy                             # optional
note: anything you want to remember   # optional, ignored
```

Each ideas file starts with an approval line, above the first entry:

```
approved: no
```

The weekly routine writes `approved: no`. Review the week, edit anything you like, then change it to `approved: yes`. **Nothing is posted until you do.** On days that are not approved the daily routine posts nothing and sends you a notification. A single entry can still be held back with `status: needs-check`.

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
