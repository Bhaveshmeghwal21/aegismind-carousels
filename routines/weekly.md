# Weekly ideas routine

You plan next week's posts for the Instagram account @theaegismind: dark, moody single-image posts about philosophy and psychology, with history now and then. Each post is one picture with one line on it, plus a caption. The owner reads your file and fills any gaps by editing it on GitHub, so write it to be edited. You are working in a clone of this repo on `main`. You start with no memory, so follow these steps in order.

Hard rules:
- Never edit or delete an existing file in `ideas/`. You only add one new file.
- Never invent a quote, a date, a number or a study. When unsure, mark the entry `needs-check` (see below).

## Steps

1. `git pull --ff-only origin main`, then `python3 -m pip install -q -r requirements.txt`.
2. Work out next week: the coming Monday in India (`TZ=Asia/Calcutta date`), and its ISO week label `YYYY-Www` (for example `2026-W49`). If `ideas/<label>.md` already exists, stop and report; do not overwrite it.
3. Read `ideas/2026-W48.md` as the exact format to copy, and read the last three files in `ideas/` so you do not repeat a topic or thinker from the past month.
4. Write `ideas/<label>.md` with exactly 7 entries, one for each day Monday to Sunday, headed `## YYYY-MM-DD`. Each entry has exactly these lines: `status`, `topic`, `hook` and `caption`. No `slides:`.
   - Mix: about three philosophy, three psychology, one history (history of ideas counts).
   - The image shows only the `topic` (a small label above) and the `hook` (the line itself), so the hook must stand alone as a strong, curious line.
   - The caption carries the explanation: three to five short sentences that tell the story or the idea, then one small thing for the reader to try, then the hashtags.
   - Fit: `topic` at most 25 characters; `hook` at most 50 characters (it must read well on two or three lines on a phone).
   - Write ideas in your own words. Quotes must be short (under 25 words), well known, correctly attributed, and name the work. A study needs its researcher or institution and year.
   - If you are not sure of a quote's wording, a date, a number or who said it, set `status: needs-check` and add a `note:` line saying what to check. Entries marked `needs-check` are never posted.
   - Use plain letters, digits, ordinary punctuation, curly quotes and em dashes only. No emoji and no non-Latin letters. Hashtags go in the caption only.
   - Hashtags: three to five, in the caption only, at the end.
5. Check it renders: for each of the 7 dates run `PYTHONPATH=src python3 -m carousel render --date DATE --out /tmp/check`. Exit 0 is good. Exit 3 is expected only for `needs-check` entries. A text-too-long or unsupported-character error means you shorten or reword that entry and run it again.
6. `git add ideas/<label>.md && git commit -m "ideas: week <label>" && git push origin main`.
7. Report: the 7 dates with topic and hook, any `needs-check` entries and what to verify, and a reminder that the owner can edit the file on GitHub before Monday.
