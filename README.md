# Daily Loose-End Digest — Kanban Proof-of-Concept

Responsive, read-only Kanban presentation of the daily task listing, built on
[**jKanban**](https://github.com/riktar/jkanban) (vanilla JS, no build, Apache-2.0, vendored under `vendor/`).

**Status: proof-of-concept with MOCK data.** Cards link to `example.com` permalinks — nothing real.

## What it proves
- **Read-only** board: `dragItems:false`, `dragBoards:false`, no add buttons.
- **Tap-to-open card links** on mobile: each card's thread link is a real `<a href target="_blank">`.
- **Responsive**: wide (`>960px`) = 6 columns side by side; narrow = boards auto-stack full-width (jKanban `responsive`/`responsivePercentage`).
- **Columns** = the digest's six status buckets: New / Progress / Yet-to-start / Stalled / Resolved / Obsolete.

## Layout
- `index.html` — the board, board data, jKanban config
- `styles.css` — theme + column accents
- `vendor/jkanban.min.css`, `vendor/jkanban.min.js` — vendored jKanban 1.x dist
- `LICENSE.jkanban` — jKanban's Apache-2.0 license (attribution)

## Serve locally
```
python3 -m http.server 8765   # then open http://localhost:8765/
```
