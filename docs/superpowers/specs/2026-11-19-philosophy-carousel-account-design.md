# Faceless philosophy/psychology carousel account: design

Date: 2026-11-19. Status: approved by the owner, then amended the same day (below).

> **Amendment, 2026-11-19 (owner's direction after reviewing the first draft look).**
> 1. **One image, not a carousel, for now.** Each post is a single 1080×1350 picture. The slide-by-slide outline and the closing slide are paused.
> 2. **Content: a quote.** The picture shows a quote by a real thinker (Marcus Aurelius, Seneca, Epictetus, Buddha, Musashi, Osho, Socrates and so on) and `— Name` under it. Every entry names its source work and translator, and the caption repeats them. Misattributed quotes are rife online, so wording is checked against the work where possible and uncertain entries are marked `needs-check` and never posted. Public-domain translations are preferred.
> 3. **Look.** Black, white and grey only, no red. A normal serif font (EB Garamond), quote about 40–66 px. The background is real public-domain art (Cleveland Museum of Art open access, CC0: Roman portrait heads, Buddhist sculpture, Rembrandt-era and baroque paintings), turned black and white, darkened, vignetted and given film grain, with a dark scrim behind the text. The art is mood, not a portrait of the thinker; captions credit the work and never claim otherwise. Copyrighted art, such as manga panels, is not used: it is the reposted, unoriginal content Instagram demotes.
> 4. Posts are `posts/YYYY-MM-DD/post.png` plus `caption.txt` (quote, source, reflection, art credit, hashtags). An earlier code-drawn landscape background was tried and replaced by the real art.
> 5. **The owner approves each week.** The weekly routine writes `approved: no` at the top of the week's file. Only after the owner changes it to `approved: yes` can the daily routine post any of that week's entries (and then only as a Metricool draft while `publish_mode` is `draft`). The routines send a phone notification when a week is waiting and on any day that is skipped.
> 6. **Thinkers are not a fixed list.** The weekly routine searches for quotes itself, from any thinker, and avoids repeating an author within 6 weeks or any quote or image.
> 7. The rest of this document still describes the original carousel plan; where they differ, this amendment wins. Posts are now `posts/YYYY-MM-DD/post.png`.

## Intent and why

The owner wants a faceless Instagram account (@theaegismind) that posts dark, bold carousels about philosophy and psychology, with history now and then. They want it to run mostly without them: a scheduled Claude session in the cloud does the weekly planning and the daily posting. The owner's only regular job is filling gaps in the weekly idea list. The account is a content experiment; no revenue goal has been stated.

## Goals

- One image carousel posted per day.
- Every week the cloud agent proposes at least 7 post ideas (topic, hook, slide-by-slide outline, caption). The owner edits, replaces or adds ideas. The daily agent posts from that list.
- Hands-off posting after setup. The owner never posts by hand.
- A consistent look, so the account is recognisable.

## Non-goals

- Growth tactics that need a human (commenting, DMs, collabs). Not automated.
- Reels, Stories or video.
- Automatic profile setup (bio, avatar). The owner does that.

## Anti-goals (a failure even if it technically works)

- Recycled or reposted images from other pages. Instagram has cut such accounts from recommendations since 30 April 2026 (secondary reports; no Meta announcement found).
- A post going live with wrong, invented or misattributed quotes or history facts.
- Any colour outside the palette during the first month.

## Decided by the owner

- Topics: philosophy and psychology; history optional.
- Format: carousels only.
- Palette: black, white and red only, for at least the first month.
- Mood: bold, moody, dark.
- Weekly flow: the agent proposes 7 or more ideas; the owner fills gaps.
- Runs as Claude scheduled cloud agents (routines), not a script the owner maintains.
- Posting goes through the Metricool connector, already connected (brand id 8209012, timezone Asia/Calcutta).

## Approaches considered

1. **Scheduled Claude routines plus Metricool connector plus a public GitHub repo (chosen).** Claude renders slides in the cloud, commits them to the repo, and gives Metricool the public image links. Trade-off: several moving parts, and some are untested (see Risks).
2. **Own script on Instagram's official API, scheduled with GitHub Actions.** Fewer unknowns once built, but the owner would have to maintain tokens and code. Rejected by the owner: they want Claude sessions to do the work.
3. **Claude only writes the content; the owner designs and posts in Canva.** Least risk, but not automated. Rejected.

## Design (my calls, flagged)

- **Repo (my call):** a free public GitHub repo, for example `aegismind-carousels`. It holds `ideas/YYYY-Www.md` (the weekly list the owner edits) and `posts/YYYY-MM-DD/slide-1.png` and so on. It must be public so Metricool and Instagram can fetch the image links.
- **Weekly routine (my call):** once a week it writes next week's ideas file (7 or more entries) and commits it. Day of week and time are for the builder; default is the weekend, so the owner has time to edit.
- **Daily routine (my call):** reads today's entry, renders 6 to 8 slides (hook, 4 to 6 idea slides, closing), commits them, then calls Metricool's `createScheduledPost` with the public image links as an Instagram `POST` carousel.
- **Slides (my call):** 1080×1350 portrait. A hook slide, 4 to 6 idea slides, a closing slide. Pure black background, white text, red accent only. Large bold type, high contrast, generous empty space. The account handle sits small on each slide.
- **First week:** every post is created with `draft: true` so the owner can review in Metricool before anything goes live. After the owner is happy, switch to automatic publishing.
- **Accuracy rule (my call):** quotes must be short, correctly attributed and well known. Where the agent is unsure of a quote or date, it must leave that fact out or mark the idea "needs owner check" in the ideas file instead of posting it.
- **AI disclosure (open, owner to decide):** Metricool exposes an `isAiGenerated` flag. The slides are rendered from templates, but the text is written by Claude. Default for now: not set. Owner to confirm.

## Risks and unknowns (to test before going automatic)

1. Whether a cloud routine can use the Metricool connector. Connectors connected on claude.ai should reach routines, but this has not been tested.
2. Whether the cloud sandbox can render slide images with good fonts. Not tested.
3. Whether Metricool accepts raw GitHub image links. Its tool says media takes "public URLs"; not tested.
4. Metricool Free plan: one source says about 20 scheduled posts; daily posting is about 30 a month. Unconfirmed whether the connector's scheduling works on Free at all. A paid plan may be needed.
5. Instagram or Meta may change its API or policies. Expect occasional maintenance.

## Test before trusting it

A single manual run that renders one carousel, commits it, and creates one Metricool draft. The owner opens the draft in Metricool and checks the look and the image links before any schedule is switched on.

## Left to the builder

Fonts and exact type sizes, the red value, slide wording style, caption and hashtag style, posting time (Metricool's best-time tool can suggest one), routine cron times, how the agent handles an empty or unreadable ideas file, and the exact prompts for the two routines.
