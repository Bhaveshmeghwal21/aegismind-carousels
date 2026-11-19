# Daily post routine

You post one Reel a day to the Instagram account @theaegismind through the Metricool connector. The Reel is the day's quote image held still for a few seconds, with a public-domain classical recording already mixed into the video. You are working in a clone of this repo on `main`. You start with no memory, so follow these steps in order.

Hard rules:
- Post only today's entry from `ideas/`. Never substitute another day's entry. Never write or change a caption, quote or fact yourself.
- If anything is unexpected, stop and report what happened. Do not improvise a workaround that posts.
- Call `createScheduledPost` at most once per run. If it errors or times out, check `getScheduledPosts` for that day before deciding anything; never create a second post.
- Do not edit `config.json`, anything in `ideas/`, or anything in `routines/`.

## Steps

1. Read `config.json`. Set DATE to today's date in India: `TZ=Asia/Calcutta date +%F`.
2. `git pull --ff-only origin main`, then `python3 -m pip install -q -r requirements.txt`. If the pinned install fails, run `python3 -m pip install -q pillow fonttools imageio-ffmpeg` (imageio-ffmpeg supplies the ffmpeg program that makes the video).
3. Render: `PYTHONPATH=src python3 -m carousel render --date DATE --reel <reel_seconds from config.json>`
   - Exit 0: stdout is a JSON list of two paths, `posts/DATE/post.png` and `posts/DATE/reel.mp4`; the finished caption (it credits the art and the music) is in `posts/DATE/caption.txt`. Continue.
   - Exit 3: nothing to post (no entry, status `needs-check`, an unknown image or music id, a malformed entry, or a week the owner has not approved yet). Stop. Report the stderr message and send a push notification (PushNotification) with it, so the owner knows. Post nothing.
   - Exit 4: this date was already posted. Stop and report.
   - Anything else: stop and report the error.
4. Publish the files so Metricool can fetch them: `git add posts/DATE && git commit -m "post: reel for DATE" && git push origin main`. If the push is rejected because main moved, `git pull --rebase origin main` and push again. If it still fails, stop and report.
5. Check the video link: `curl -sI https://raw.githubusercontent.com/Bhaveshmeghwal21/aegismind-carousels/main/posts/DATE/reel.mp4`. It must answer with a 200 status (its content type may show `application/octet-stream`; that is fine). The link can lag a few seconds after a push: retry up to 5 times, 10 seconds apart. If it is still not 200, stop and report. Do not call Metricool.
6. Duplicate check: call `getScheduledPosts` for `brand_id` for DATE (00:00 to 23:59, timezone from config). If a post whose text starts with the same first line as `posts/DATE/caption.txt` already exists, stop and report.
7. Read the caption from `posts/DATE/caption.txt` and use its whole text exactly, line breaks included. Do not edit it. Call `createScheduledPost` with:
   - `blogId`: `brand_id` as a string
   - `date`: DATE plus `post_time` from config as ISO 8601 with the +05:30 offset, for example `2026-11-23T19:00:00+05:30`. If that time has already passed today, use ten minutes from now instead.
   - `info`: a JSON string with `autoPublish` true; `draft` true unless `publish_mode` in config is `auto`; `text` set to the caption; `media` set to a list with the one video link from step 5; `providers` set to `[{"network":"instagram"}]`; `publicationDate` set to `{"dateTime":"DATEThh:mm:00","timezone":"Asia/Calcutta"}` using `post_time`; `instagramData` set to `{"type":"REEL","showReelOnFeed":true,"isAiGenerated":<is_ai_generated from config>}` (do not set `audioConfiguration`: the music is already inside the video); plus the empty defaults `descendants: []`, `firstCommentText: ""`, `hasNotReadNotes: false`, `mediaAltText: []`, `shortener: false`, `smartLinkData: {"ids": []}`.
8. On success the result includes a `plannerUrl`. Run `PYTHONPATH=src python3 -m carousel mark-posted --date DATE --mode <draft or auto, as used> --url <plannerUrl>`, then `git add posts/DATE/posted.json && git commit -m "post: mark DATE posted" && git push origin main`.
9. Send a push notification (PushNotification) so the owner can review: "Draft ready for DATE: <author>. Open <plannerUrl>, check the image and caption, and schedule it in Metricool before <post_time> IST, or delete it to reject." Use the real values.
10. Finish with one short report: the date, the quote's author, draft or auto, and the `plannerUrl`.
