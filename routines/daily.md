# Daily post routine

You post one carousel a day to the Instagram account @theaegismind through the Metricool connector. You are working in a clone of this repo on `main`. You start with no memory, so follow these steps in order.

Hard rules:
- Post only today's entry from `ideas/`. Never substitute another day's entry. Never write or change a caption, quote or fact yourself.
- If anything is unexpected, stop and report what happened. Do not improvise a workaround that posts.
- Call `createScheduledPost` at most once per run. If it errors or times out, check `getScheduledPosts` for that day before deciding anything; never create a second post.
- Do not edit `config.json`, anything in `ideas/`, or anything in `routines/`.

## Steps

1. Read `config.json`. Set DATE to today's date in India: `TZ=Asia/Calcutta date +%F`.
2. `git pull --ff-only origin main`, then `python3 -m pip install -q -r requirements.txt`. If the pinned install fails, run `python3 -m pip install -q pillow fonttools`.
3. Render: `PYTHONPATH=src python3 -m carousel render --date DATE`
   - Exit 0: stdout is a JSON list of slide paths (`posts/DATE/slide-1.png` and so on). Continue.
   - Exit 3: nothing to post (no entry, status `needs-check`, wrong slide count, or a malformed entry). Stop. Report the stderr message. Post nothing.
   - Exit 4: this date was already posted. Stop and report.
   - Anything else: stop and report the error.
4. Publish the slides so Metricool can fetch them: `git add posts/DATE && git commit -m "post: slides for DATE" && git push origin main`. If the push is rejected because main moved, `git pull --rebase origin main` and push again. If it still fails, stop and report.
5. Check every slide link, for N from 1 to the number of slides: `curl -sI https://raw.githubusercontent.com/Bhaveshmeghwal21/aegismind-carousels/main/posts/DATE/slide-N.png`. Each must answer with a 200 status and `content-type: image/png`. The link can lag a few seconds after a push: retry up to 5 times, 10 seconds apart. If it is still not 200, stop and report. Do not call Metricool.
6. Duplicate check: call `getScheduledPosts` for `brand_id` for DATE (00:00 to 23:59, timezone from config). If a post with the same caption text already exists, stop and report.
7. Read the caption for DATE from the `caption:` line of its entry in `ideas/`. Call `createScheduledPost` with:
   - `blogId`: `brand_id` as a string
   - `date`: DATE plus `post_time` from config as ISO 8601 with the +05:30 offset, for example `2026-11-23T19:00:00+05:30`. If that time has already passed today, use ten minutes from now instead.
   - `info`: a JSON string with `autoPublish` true; `draft` true unless `publish_mode` in config is `auto`; `text` set to the caption; `media` set to the slide links, in order, from step 5; `providers` set to `[{"network":"instagram"}]`; `publicationDate` set to `{"dateTime":"DATEThh:mm:00","timezone":"Asia/Calcutta"}` using `post_time`; `instagramData` set to `{"type":"POST","isAiGenerated":<is_ai_generated from config>}`; plus the empty defaults `descendants: []`, `firstCommentText: ""`, `hasNotReadNotes: false`, `mediaAltText: []`, `shortener: false`, `smartLinkData: {"ids": []}`.
8. On success the result includes a `plannerUrl`. Run `PYTHONPATH=src python3 -m carousel mark-posted --date DATE --mode <draft or auto, as used> --url <plannerUrl>`, then `git add posts/DATE/posted.json && git commit -m "post: mark DATE posted" && git push origin main`.
9. Finish with one short report: the date, the topic, draft or auto, and the `plannerUrl`.
