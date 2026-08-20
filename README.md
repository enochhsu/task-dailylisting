# Daily Loose-End Digest — Kanban (task-dailylisting)

Responsive, read-only, **archival** Kanban presentation of the daily task listing, built on
[**jKanban**](https://github.com/riktar/jkanban) (vanilla JS, no build, Apache-2.0, vendored under `vendor/`).

**Live data** (not mock): each board is generated from the real daily loose-end digest via `emit_kanban.py`.

## Layout (archival)
- `index.html` — **archive index** (paginated; each day, newest first)
- `day/YYYY-MM-DD/index.html` — one board **per day**, compiled fresh, **never overwritten** (temporal archive)
- `styles.css`, `vendor/` — shared theme + vendored jKanban
- `emit_kanban.py` — parses `digest.txt` → renders the day board + rebuilds the index.
  **Not yet wired into any cron** — run manually:
  ```
  python3 emit_kanban.py --digest ~/.hermes/cache/slack_corpus/digest.txt --date 2026-08-19
  python3 emit_kanban.py --update-index          # rebuild archive index from day/
  ```
- `robots.txt` (`Disallow: /`) + `<meta name="robots" content="noindex,nofollow">` on every page → not indexed by Google.

## What it demonstrates
- **Read-only**: `dragItems:false`, `dragBoards:false`, no add buttons.
- **Tap-to-open card links** on mobile: each card's thread link is a real `<a href>` to the exact Slack thread.
- **Responsive**: wide (`>960px`) = columns side by side (CSS Grid auto-fit, fills row); phone = single stacked column.
- **Columns** = the digest's buckets present that day (New / In-progress(quiet) / Progress / Yet-to-start / Stalled / Resolved / Obsolete).
- **Card content**: channel name + loose-end excerpt + stale-clock meta (`open · idle · decision`) + Slack thread link.

## Access / privacy
Public on GitHub Pages (reachable by anyone with the URL; not indexed by search engines).
Real loose-end content and Slack thread permalinks are published — this is accepted for the
short, non-sensitive card text, but avoid adding sensitive/long content to the digest.

## Serve locally
```
python3 -m http.server 8769   # then open http://localhost:8769/
```
