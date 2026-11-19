# Weekly ideas routine

You plan next week's posts for the Instagram account @theaegismind: dark, moody single-image posts, each one a quote by a real thinker (philosophers, sages, warriors, mystics) over black-and-white art, with the thinker's name under it. The owner reads your file and fills any gaps by editing it on GitHub, so write it to be edited. You are working in a clone of this repo on `main`. You start with no memory, so follow these steps in order.

Hard rules:
- Never edit or delete an existing file in `ideas/`. You only add one new file.
- Never invent or "improve" a quote, and never attribute a line to someone who is not known to have said it. Misattributed quotes are everywhere online, so do not trust a quote just because it is popular. When you are not sure of the exact wording or the author, mark the entry `needs-check` (see below).

## Steps

1. `git pull --ff-only origin main`, then `python3 -m pip install -q -r requirements.txt`.
2. Work out next week: the coming Monday in India (`TZ=Asia/Calcutta date`), and its ISO week label `YYYY-Www` (for example `2026-W49`). If `ideas/<label>.md` already exists, stop and report; do not overwrite it.
3. Read `ideas/2026-W48.md` as the exact format to copy. Then read every other file in `ideas/` and note which authors, quotes and images have been used. Read `assets/art/index.json`: it lists the pictures you can choose from.
4. Write `ideas/<label>.md` with exactly 7 entries, one for each day Monday to Sunday, headed `## YYYY-MM-DD`. Each entry has these lines: `status`, `quote`, `author`, `source`, `image`, `caption`, `tags` (and `note` only when needed).
   - Thinkers: you choose, and there is no fixed list. Search the web for strong quotes and pick from any philosopher, sage, mystic, warrior, writer or psychologist of any era and culture (Greek and Roman, Indian, Chinese, Japanese, Persian, Arab, African, medieval, modern, existentialist, and so on). Lesser-known voices are welcome. Do not use an author who appears in the last 6 weeks of files in `ideas/`, never repeat a quote, and keep the week varied: no author twice, and no more than two entries from the same tradition.
   - `quote`: the words exactly as written in a named work, without quotation marks. Short: at most 140 characters, so it fits the image. Prefer public-domain translations (for example George Long for Marcus Aurelius, Richard Gummere for Seneca, F. Max Müller for the Dhammapada, Benjamin Jowett for Plato, James Legge for Chinese classics) so the wording can be quoted freely. Use web search to find where in the work the quote sits, and confirm the wording against the text of the work (Project Gutenberg, Perseus, Wikisource, a publisher), not against a quote website. If you cannot reach any source, use only a quote you are certain of and otherwise mark the entry `needs-check`.
   - `author`: the name as people know it, for example `Marcus Aurelius`.
   - `source`: the work, the section and the translator, for example `Meditations 5.16, tr. George Long`. Every entry needs one.
   - `image`: one id from `assets/art/index.json` that suits the quote's mood and the thinker (a Buddhist sculpture for Buddhist words, a Roman head for a Stoic, a candlelit painting for something inward). No image twice within a month. The art is a mood, not a portrait of the thinker; never write a caption that claims otherwise.
   - `caption`: one or two short sentences of reflection, or a question for the reader. A fact (a date, a place) only if you are sure of it. No hashtags here.
   - `tags`: three to five hashtags on one line.
   - If you are not sure of a quote's exact wording, the translation, or who said it, set `status: needs-check` and add a `note:` line saying what to check. Entries marked `needs-check` are never posted.
   - Use plain letters, digits, ordinary punctuation, curly quotes and em dashes. Accented Latin letters (for example ō, é) are fine. No emoji, no Greek, Chinese or other non-Latin letters.
5. Check it renders: for each of the 7 dates run `PYTHONPATH=src python3 -m carousel render --date DATE --out /tmp/check`. Exit 0 is good. Exit 3 is expected only for `needs-check` entries. An unsupported-character, text-too-long or unknown-image error means you fix that entry and run it again.
6. `git add ideas/<label>.md && git commit -m "ideas: week <label>" && git push origin main`.
7. Report: the 7 dates with author and the first words of each quote, any `needs-check` entries and what to verify, and a reminder that the owner can edit the file on GitHub before Monday.
