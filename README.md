# aegismind-carousels

Content and tooling for the Instagram account @theaegismind: black-and-white manga-ink posts. Each post is a quote by a real thinker (Marcus Aurelius, Seneca, Buddha, Musashi, Osho, Socrates and so on) in a heavy serif at the top of a white page, with the thinker and the work under it and an original ink illustration below. The repo name says carousels because that was the first plan; for now every post is one picture.

## How it works

- `ideas/YYYY-Www.md`: one file per week, one entry per day. A weekly Claude routine drafts the next week; you edit or add entries on GitHub.
- `assets/art/`: the art library. The `ink-*` entries (`"kind": "ink"`) are original black-and-white ink illustrations made with AI (Figma's image generator); they are what posts use now, and because they are AI-made `is_ai_generated` in `config.json` is `true` so Instagram labels the posts. The older entries are public-domain museum photos (Cleveland Museum of Art open access, CC0) that render in the earlier dark photo style. `index.json` has each picture's focus point and credit. Each post uses the entry's `image:` id, or one picked by date.
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

To add illustrations: save a 4:3 black-ink-on-white picture (no text in it) as `assets/art/<id>.png` and add an `index.json` entry copied from an `ink-*` one. Prompt idea: `Black ink manga illustration on a plain white background. An original character: ... Strictly pure black and white, no colour, no grey wash, no text, no speech bubbles, no signature, no watermark.` Name no artist, series or character.

Music with `"license": "CC BY 4.0"` (Kevin MacLeod, incompetech.com) needs the credit `music_credit` writes into the caption, so never remove the caption's music line.

The font is EB Garamond (SIL Open Font License 1.1), in `assets/fonts/`. Artwork credits are in `assets/art/index.json` and in every caption.
