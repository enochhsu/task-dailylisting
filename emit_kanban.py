#!/usr/bin/env python3
"""emit_kanban.py — render the daily loose-end digest as a jKanban board.

Parses ~/.hermes/cache/slack_corpus/digest.txt and writes day/<date>/index.html,
then regenerates the root index.html archive manifest from the day/ directory.
Standalone for now (NOT wired into any cron yet).

Usage:
  python3 emit_kanban.py --digest <path>          # board for this digest (date from header)
  python3 emit_kanban.py --update-index           # only rebuild the archive manifest
"""
import re, html, argparse, os
from datetime import datetime

# canonical column order: id -> (title, digest header keywords)
COLUMNS = [
    ("new",      "New today",            ("new today",)),
    ("progress", "Progress today",       ("progress today",)),
    ("quiet",    "In progress (quiet)",  ("in progress",)),
    ("yet",      "Yet to start",         ("yet to start",)),
    ("stalled",  "Stalled >7d",          ("stalled",)),
    ("resolved", "Resolved today",       ("resolved today",)),
    ("obsolete", "Marked obsolete",      ("obsolete",)),
]


def match_column(low):
    """Return column id whose keyword appears in a (lowercased) header line, or None."""
    for cid, title, kws in COLUMNS:
        if any(k in low for k in kws):
            return cid
    return None


def parse_item(s):
    """Parse one digest bullet into a card dict."""
    s = re.sub(r"^[•🟨🟦]\s*", "", s)
    m = re.match(r"^#([^\s:]+)", s)               # channel token
    chan = m.group(1) if m else ""
    rest = s[m.end():] if m else s
    rest = rest.lstrip(" :")
    urls = re.findall(r"https?://\S+", rest)        # permalink = last URL
    perm = urls[-1] if urls else ""
    if perm:
        rest = rest.replace(perm, "")
    clocks = ""
    cm = re.search(r"(open\s+\S+d\s+·\s+idle\s+\S+d\s+·\s+decision\s+\S+d)", rest)
    if cm:
        clocks = cm.group(1)
        rest = rest[: cm.start()]
    excerpt = re.sub(r"\s+", " ", rest).strip(" —•｜|")
    return {"chan": chan, "excerpt": excerpt, "clocks": clocks,
            "permalink": html.escape(perm, quote=True)}


def parse_digest(path):
    """Return list of (column_id, [item,...]) in digest order (empty only if none)."""
    secs, current = [], None
    cur = []
    for raw in open(path, encoding="utf-8"):
        s = raw.strip()
        if not s:
            continue
        cid = match_column(s.lower())
        if cid and not s.startswith(("•", "🟨", "🟦")):
            if current:
                secs.append((current, cur))
            current, cur = cid, []
            continue
        if current and s.startswith(("•", "🟨", "🟦")):
            it = parse_item(s)
            if it.get("excerpt") or it.get("permalink"):
                cur.append(it)
    if current:
        secs.append((current, cur))
    return secs


def build_boards(secs):
    """Order sections by COLUMNS and return the jKanban boards list."""
    by = {cid: items for cid, items in secs}
    boards = []
    for cid, title, _ in COLUMNS:
        items = by.get(cid) or []
        if not items:
            continue
        board = {"id": "col-" + cid, "class": "col-" + cid, "title": title, "item": []}
        for i, it in enumerate(items):
            meta = '<div class="meta">%s</div>' % it["clocks"] if it["clocks"] else ""
            board["item"].append({
                "id": "%s-%d" % (cid, i),
                "class": "",
                "title": ('<div class="chan">%s</div>'
                          '<div class="excerpt">%s</div>%s'
                          '<a class="open" href="%s" target="_blank" rel="noopener">open thread &#8599;</a>')
                          % (html.escape(it["chan"] or "?"), html.escape(it["excerpt"]),
                             meta, it["permalink"]),
            })
        boards.append(board)
    return boards


DAY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Daily Loose-End Digest · Kanban — {date}</title>
<link rel="stylesheet" href="../../styles.css?v=3">
</head>
<body>

<div class="topbar">
  <h1>Daily Loose-End Digest</h1>
  <span class="tag">archived kanban · read-only</span>
  <span class="note">{label} · cutoff 18:00</span>
</div>

<div class="wrap">
  <div id="board"></div>
</div>

<div class="footer">
  Archive entry for {date}. Read-only (<code>dragItems/dragBoards=false</code>); each card = a loose-end from the
  daily 18:30 digest (channel + excerpt + thread link, tap-to-open on mobile).
  <br><a href="../../">&#8592; Archive index</a>
</div>

<script src="../../vendor/jkanban.min.js"></script>
<script>
var kanban = new jKanban({{
  element: '#board',
  gutter: '12px',
  responsive: '960',
  responsivePercentage: true,
  dragBoards: false,
  dragItems: false,
  itemAddOptions: {{ enabled: false }},
  propagationHandlers: ['click'],
  boards: {boards_json}
}});
document.querySelectorAll('.kanban-board').forEach(function (b) {{
  var c = b.querySelectorAll('.kanban-item').length;
  var s = document.createElement('span'); s.className = 'count'; s.textContent = c;
  b.querySelector('header .kanban-title-board').appendChild(s);
}});
</script>
</body>
</html>
"""


def label_for(date):
    return datetime.strptime(date, "%Y-%m-%d").strftime("%a %d %b %Y")


def render_day(day_html_dir, date, boards, out_dir="."):
    import json as _json
    d = os.path.join(out_dir, "day", date)
    os.makedirs(d, exist_ok=True)
    html_str = DAY_TEMPLATE.format(
        date=date, label=label_for(date),
        boards_json=_json.dumps(boards, ensure_ascii=False))
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_str)
    return os.path.join(d, "index.html")


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Daily Loose-End Digest · Kanban — Archive</title>
<link rel="stylesheet" href="styles.css?v=3">
<style>
  .archive {{ padding: 18px; max-width: 640px; margin: 0 auto; }}
  .archive h2 {{ font-size: 16px; margin: 0 0 12px; }}
  .archive ul {{ list-style: none; padding: 0; margin: 0; }}
  .archive li {{ background: #fff; border: 1px solid #e4e7ec; border-radius: 8px;
    padding: 12px 14px; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }}
  .archive li a {{ font-weight: 600; color: #0a66c2; text-decoration: none; font-size: 15px; }}
  .archive li .d {{ color: #5e6c84; font-size: 13px; margin-left: auto; }}
  .pager {{ display: flex; gap: 8px; align-items: center; margin-top: 14px; font-size: 13px; }}
  .pager button {{ border: 1px solid #c8d7ee; background:#fff; color:#0a66c2; border-radius:6px;
    padding: 6px 12px; cursor:pointer; font-weight:600; }}
  .pager button:disabled {{ opacity:.4; cursor:default; }}
  .pager .info {{ color:#5e6c84; }}
</style>
</head>
<body>

<div class="topbar">
  <h1>Daily Loose-End Digest · Kanban</h1>
  <span class="tag">archive index</span>
  <span class="note">one board per day — newest first</span>
</div>

<div class="archive">
  <h2>Archives</h2>
  <ul id="list"></ul>
  <div class="pager">
    <button id="prev" type="button">&#8592; Newer</button>
    <span class="info" id="pageinfo"></span>
    <button id="next" type="button">Older &#8594;</button>
  </div>
</div>

<script>
var DAYS = {days_json};
var PAGE = 14;
(function () {{
  var page = 0, list = document.getElementById('list');
  var pi = document.getElementById('pageinfo'), pr = document.getElementById('prev'), nx = document.getElementById('next');
  var pages = Math.max(1, Math.ceil(DAYS.length / PAGE));
  function render() {{
    list.innerHTML = '';
    DAYS.slice(page*PAGE, (page+1)*PAGE).forEach(function (d) {{
      var li = document.createElement('li');
      var a = document.createElement('a'); a.href = 'day/' + d.date + '/'; a.textContent = d.label;
      var s = document.createElement('span'); s.className = 'd'; s.textContent = d.date;
      li.appendChild(a); li.appendChild(s); list.appendChild(li);
    }});
    var st = page*PAGE + 1, en = Math.min(DAYS.length, (page+1)*PAGE);
    pi.textContent = DAYS.length === 0 ? 'no entries' : 'Showing ' + st + '\u2013' + en + ' of ' + DAYS.length;
    pr.disabled = page === 0; nx.disabled = page >= pages - 1;
  }}
  pr.addEventListener('click', function () {{ if (page > 0) {{ page--; render(); }} }});
  nx.addEventListener('click', function () {{ if (page < pages - 1) {{ page++; render(); }} }});
  render();
}})();
</script>
</body>
</html>
"""


def update_index(out_dir="."):
    import json as _json
    day_root = os.path.join(out_dir, "day")
    days = []
    if os.path.isdir(day_root):
        for name in os.listdir(day_root):
            d = os.path.join(day_root, name)
            if os.path.isdir(d) and re.match(r"^\d{4}-\d{2}-\d{2}$", name):
                days.append({"date": name, "label": label_for(name)})
    days.sort(key=lambda x: x["date"], reverse=True)
    html_str = INDEX_TEMPLATE.format(days_json=_json.dumps(days, ensure_ascii=False))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_str)
    return days


def digest_date(path):
    for raw in open(path, encoding="utf-8"):
        m = re.search(r"\b(\d{2})\s+([A-Za-z]{3})\b", raw)
        if m:
            return datetime.strptime(m.group(0), "%d %b").replace(year=datetime.now().year)
    return datetime.now()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digest", help="path to digest.txt")
    ap.add_argument("--date", help="archive date YYYY-MM-DD (default: derived)")
    ap.add_argument("--update-index", action="store_true")
    a = ap.parse_args()

    if a.update_index:
        days = update_index()
        print("index rebuilt:", [d["date"] for d in days])
        return

    if not a.digest:
        raise SystemExit("provide --digest <path> (or --update-index)")
    secs = parse_digest(a.digest)
    boards = build_boards(secs)
    date = a.date or digest_date(a.digest).strftime("%Y-%m-%d")
    p = render_day(None, date, boards)
    days = update_index()
    print("wrote", p)
    print("columns:", [(b["id"], len(b["item"])) for b in boards])
    print("archive:", [d["date"] for d in days])


if __name__ == "__main__":
    main()
