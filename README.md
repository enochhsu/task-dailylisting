# Daily Loose-End Digest — Kanban Proof-of-Concept

Responsive, read-only, **archival** Kanban presentation of the daily task listing, built on
[**jKanban**](https://github.com/riktar/jkanban) (vanilla JS, no build, Apache-2.0, vendored under `vendor/`).

**Status: proof-of-concept with MOCK data.** Cards link to dummy permalinks — nothing real.

## Layout (archival)
- `index.html` — **archive index** (lists each day, newest first)
- `day/YYYY-MM-DD/index.html` — one board **per day**; each day is compiled fresh and **never overwritten**, so the board doubles as a temporal archive (diff a task's movement across days)
- `styles.css`, `vendor/` — shared theme + vendored jKanban

## What it demonstrates
- **Read-only**: `dragItems:false`, `dragBoards:false`, no add buttons.
- **Tap-to-open card links** on mobile: each card's thread link is a real `<a href target="_blank">`.
- **Responsive**: wide (`>960px`) = 6 columns; narrow = boards auto-stack full-width (jKanban `responsive`/`responsivePercentage`).
- **Columns** = the digest's six status buckets: New / Progress / Yet-to-start / Stalled / Resolved / Obsolete.
- **Card content follows the 18:30 digest**: channel name (not a hashtag) + the loose-end excerpt; in production the "open thread" link is the exact Slack thread permalink (`?thread_ts=&channel=&message_ts=` form).

## Access
Public GitHub Pages (mock only). Real work items are **not** publishable publicly —
see the appraised options for private-only access (Tailscale-gated hosting is the
recommended private route; GitHub Pages cannot restrict a site to one individual account).

## Serve locally
```
python3 -m http.server 8766   # then open http://localhost:8766/
```
