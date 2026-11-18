# Philosophy Carousel Account Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A small fixed slide-maker plus two scheduled cloud routines that plan and post one dark black/white/red carousel a day to @theaegismind through Metricool.

**Architecture:** The repo `Bhaveshmeghwal21/aegismind-carousels` (public) holds a Python slide renderer, the weekly ideas files the owner edits, and the routine prompts. The weekly routine writes next week's ideas. The daily routine runs the renderer, pushes the PNGs, and calls Metricool's `createScheduledPost` with the raw GitHub image links. A fixed renderer keeps every post looking the same; the cloud agent only runs it.

**Tech Stack:** Python 3, Pillow, fontTools (glyph check), pytest, `gh`/git, Claude routines (RemoteTrigger), Metricool connector.

**Spec:** `docs/superpowers/specs/2026-11-19-philosophy-carousel-account-design.md`

## Global Constraints

- Slides are 1080×1350 portrait PNG. Carousel is 6 to 8 slides: hook, 4 to 6 idea slides, closing.
- Only black, white and red for at least the first month. Black `(0,0,0)`, white `(255,255,255)`, red `(230,0,0)`.
- Bold, moody, dark look. Pure black background, white text, red accent only. Account handle `@theaegismind` small on every slide.
- Repo must stay public so Metricool and Instagram can fetch image links.
- Metricool brand id `8209012`, timezone `Asia/Calcutta`, Instagram type `POST`.
- First week: every Metricool post is created with `draft: true`.
- Never post a quote or fact the agent is unsure of; such entries are marked `needs-check` and are never posted.
- Local clone lives at `D:\content creation\aegismind-carousels`. Cloud routines clone the repo themselves.

## Review Focus

- A long hook or body that would run off the slide: text must wrap and shrink, never clip. Pinned in Task 1.
- Quotes with curly quotes, em dashes or accents, or a character the font lacks: render the first, fail loudly on the second. Pinned in Task 1.
- An ideas entry missing a field, or no entry for today: skip and report, never post garbage and never repeat yesterday. Pinned in Task 2 and Task 3.
- The routine running twice in one day: must not create two posts. Pinned in Task 3.
- An entry marked `needs-check`: must never be posted. Pinned in Task 2.

---

## File Structure

- `config.json`: brand id, timezone, post time, `publish_mode` (`draft` or `auto`), `is_ai_generated`, closing line.
- `src/carousel/models.py`: `Slide`, `Idea` dataclasses.
- `src/carousel/errors.py`: `IdeaParseError`, `UnsupportedGlyphError`.
- `src/carousel/palette.py`: colour constants.
- `src/carousel/render.py`: slide and carousel rendering.
- `src/carousel/ideas.py`: ideas file parsing and selection.
- `src/carousel/cli.py`, `src/carousel/__main__.py`: command line used by the routines.
- `assets/fonts/`: Anton-Regular.ttf (headlines) and Inter-Regular.ttf (body), both SIL Open Font License.
- `ideas/YYYY-Www.md`, `posts/YYYY-MM-DD/`: weekly ideas; rendered slides plus `posted.json`.
- `routines/weekly.md`, `routines/daily.md`: the prompts the routines follow. Editing these files changes routine behaviour without recreating the routines.

### Task 1: Project setup and slide renderer

**Files:**
- Create: `requirements.txt`, `src/carousel/{models,errors,palette,render}.py`, `assets/fonts/*.ttf`, `tests/test_render.py`
- Work in: a clone made with `gh repo clone Bhaveshmeghwal21/aegismind-carousels "D:\content creation\aegismind-carousels"`

**Interfaces:**
- Produces: `models.Slide(title: str, body: str)`; `models.Idea(date: str, status: str, topic: str, hook: str, slides: list[Slide], caption: str)`; `render.render_slide(kind: str, title: str, body: str, index: int, total: int) -> PIL.Image.Image` where `kind` is `"hook"`, `"idea"` or `"closing"`; `render.render_carousel(idea: Idea, out_dir: Path, closing_line: str) -> list[Path]` writing `slide-1.png` to `slide-N.png`, N = `len(idea.slides) + 2`; `errors.UnsupportedGlyphError(ValueError)`.

- [ ] **Step 1:** Clone the repo, confirm `python --version` is 3.10 or newer, create a virtualenv, and install `pillow`, `fonttools`, `pytest` (record them in `requirements.txt`). Download Anton and Inter (OFL) into `assets/fonts/`.
- [ ] **Step 2: Write failing tests in `tests/test_render.py`:**
  - `test_slide_is_1080x1350`: `render_slide("hook","Why Stoics expected the worst","",1,7).size == (1080,1350)`.
  - `test_only_black_white_red_family`: for every pixel `(r,g,b)` of an idea slide, `g == b and r >= g` (anti-aliased blends of the three colours satisfy this); and at least one pure red `(230,0,0)` and one pure white pixel exist.
  - `test_long_text_never_overflows_margins`: a 400-character body; pixels with `x < 60` or `x >= 1020` are all `(0,0,0)`.
  - `test_curly_quotes_accents_dashes_render`: title `Nietzsche’s “abyss” — café, naïve` renders without raising.
  - `test_missing_glyph_raises`: title `漢字` raises `UnsupportedGlyphError`.
  - `test_carousel_slide_count`: an Idea with 5 slides writes 7 files, named `slide-1.png` to `slide-7.png`.
- [ ] **Step 3:** Run `pytest tests/test_render.py -v`. Expected: all FAIL (modules missing).
- [ ] **Step 4:** Implement the interfaces above. Look: hook slide has the hook in large white Anton with a short red bar above it; idea slides have the title in red Anton and the body in white Inter; closing slide shows `closing_line`; `index/total` and `@theaegismind` sit small at the bottom. Wrap text to the 60px margins and shrink the font size until it fits. Check every character against the font's cmap (fontTools) before drawing.
- [ ] **Step 5:** Run `pytest tests/test_render.py -v`. Expected: all PASS. Open one rendered slide and one 7-slide carousel and look at them.
- [ ] **Step 6:** Commit.

### Task 2: Ideas file parser

**Files:**
- Create: `src/carousel/ideas.py`, `tests/test_ideas.py`, `ideas/2026-W48.md` (a real first week of at least 7 entries, written by hand)

**Interfaces:**
- Consumes: `models.Idea`, `models.Slide`, `errors.IdeaParseError`.
- Produces: `ideas.parse_ideas(text: str) -> list[Idea]`; `ideas.load_ideas(ideas_dir: Path) -> list[Idea]`; `ideas.idea_for_date(ideas: list[Idea], date: str) -> Idea | None`; `ideas.is_postable(idea: Idea) -> bool` (status is `ready` and 4 to 6 slides).

File format, one entry per date:

```
## 2026-11-23
status: ready            # or: needs-check
topic: Stoicism
hook: Seneca rehearsed disaster every morning
slides:
- Premeditatio malorum :: Imagine the worst before it comes, so it cannot ambush you.
- ...
caption: One short caption. #stoicism #philosophy
```

- [ ] **Step 1: Write failing tests in `tests/test_ideas.py`:** `test_parses_valid_entry` (all fields, 5 slides); `test_missing_hook_raises_with_date` (`IdeaParseError` whose message contains the entry's date); `test_idea_for_date_returns_none_when_absent`; `test_needs_check_is_not_postable`; `test_three_slides_is_not_postable`.
- [ ] **Step 2:** Run `pytest tests/test_ideas.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement the interfaces above. Slide lines split on the first ` :: `.
- [ ] **Step 4:** Run `pytest -v` for the whole suite. Expected: PASS. Commit.

### Task 3: Command line and double-post guard

**Files:**
- Create: `src/carousel/cli.py`, `src/carousel/__main__.py`, `tests/test_cli.py`

**Interfaces:**
- Consumes: `ideas.load_ideas`, `ideas.idea_for_date`, `ideas.is_postable`, `render.render_carousel`.
- Produces: `cli.already_posted(posts_dir: Path, date: str) -> bool` (true when `posts/<date>/posted.json` exists); `cli.mark_posted(posts_dir: Path, date: str, mode: str, planner_url: str) -> Path`; command `python -m carousel render --date D --ideas ideas --out posts` printing a JSON list of slide paths; command `python -m carousel mark-posted --date D --posts posts --mode draft --url URL`. Exit codes: `0` rendered, `3` no postable idea for that date, `4` already posted.

- [ ] **Step 1: Write failing tests in `tests/test_cli.py`:** `test_render_prints_slide_paths_and_exits_0`; `test_no_entry_for_date_exits_3_and_writes_nothing`; `test_needs_check_entry_exits_3`; `test_already_posted_exits_4` (after `mark_posted`, running render again exits 4 and re-renders nothing).
- [ ] **Step 2:** Run `pytest tests/test_cli.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement the interfaces above. `render` reads `closing_line` from `config.json`.
- [ ] **Step 4:** Run `pytest -v`. Expected: all PASS. Commit and push to `main`.

### Task 4: Config and routine prompts

**Files:**
- Create: `config.json`, `routines/weekly.md`, `routines/daily.md`, update `README.md`

**Interfaces:**
- Consumes: the CLI from Task 3 and its exit codes.
- Produces: `config.json` with keys `brand_id` (8209012), `timezone` (`Asia/Calcutta`), `post_time` (`19:00`, local), `publish_mode` (`draft`), `is_ai_generated` (`false`), `closing_line` (`Follow for more.`). Two prompt files.

- [ ] **Step 1:** Write `routines/daily.md`. It tells the agent, in order: `git pull`; run `python -m carousel render --date <today IST>`; on exit 3 or 4, stop and report why, post nothing; otherwise commit and push `posts/<date>/`; confirm each raw link `https://raw.githubusercontent.com/Bhaveshmeghwal21/aegismind-carousels/main/posts/<date>/slide-N.png` answers HTTP 200 as an image before continuing; call `createScheduledPost` for `brand_id` at today's `post_time` with `providers [{"network":"instagram"}]`, `instagramData {"type":"POST"}`, the slide links as `media`, the caption as `text`, `draft` true unless `publish_mode` is `auto`, and `isAiGenerated` from config; check `getScheduledPosts` for that day does not already hold a post for the account before creating; then run `mark-posted` and push.
- [ ] **Step 2:** Write `routines/weekly.md`. It tells the agent to write `ideas/<next ISO week>.md` with at least 7 entries (one per day), mostly philosophy and psychology with history now and then, each entry in the Task 2 format; to use only short, well-known, correctly attributed quotes and to mark any entry it is unsure about `needs-check`; to never edit the owner's existing entries; and to commit and push to `main`.
- [ ] **Step 3:** Commit and push. Confirm both prompt files are on `main` on GitHub.

### Task 5: Manual test draft (owner checks it)

**Files:** none new.

- [ ] **Step 1:** In the local clone, follow `routines/daily.md` by hand for one entry from `ideas/2026-W48.md` with `publish_mode` `draft`. Confirm the raw links load in a browser tab.
- [ ] **Step 2:** Confirm `getScheduledPosts` shows the draft, give the owner its `plannerUrl`, and wait for the owner to open it in Metricool and say whether the look and links are right.
- [ ] **Step 3:** Note whether Metricool's Free plan allowed it. If not, tell the owner exactly what the limit was before any payment is suggested.

### Task 6: Create the routines

**Files:** none; uses RemoteTrigger.

**Interfaces:**
- Consumes: owner approval from Task 5, a repo the cloud can reach.

- [ ] **Step 1:** Create two routines with `RemoteTrigger`, source repo `https://github.com/Bhaveshmeghwal21/aegismind-carousels`, model `claude-sonnet-5-5`: a weekly one whose prompt is "Read routines/weekly.md and follow it", and a daily one whose prompt is "Read routines/daily.md and follow it". Convert the owner's local times (Asia/Kolkata) to UTC cron and confirm them with the owner before creating.
- [ ] **Step 2:** Run the daily routine once with `run`, then read its run log. Expected: it created a draft, or it stopped with a clear reason. Fix the prompt file if the connector or repo access failed.
- [ ] **Step 3:** After the first week of reviewed drafts, with the owner's yes, change `publish_mode` to `auto` in `config.json`.
