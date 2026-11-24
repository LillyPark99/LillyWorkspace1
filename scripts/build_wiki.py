"""wiki/**/*.md 를 오프라인에서 열리는 HTML 파일 하나(output/wiki.html)로 만든다.

실행: python3 scripts/build_wiki.py
- 외부 자원(CDN, 웹폰트, 외부 스크립트)을 쓰지 않는다. CSS·JS는 모두 HTML 안에 넣는다.
- Python 3.9에서 동작하도록 작성했다.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
OUT = ROOT / "output" / "wiki.html"

CATEGORIES = [
    ("accounts", "계정·시스템"),
    ("work", "업무 절차"),
    ("people", "사람·담당자"),
    ("terms", "용어·약어"),
    ("projects", "프로젝트"),
    ("journal", "업무 일지"),
]
HOME = "목차"

FRONT_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
TAG_RE = re.compile(r"<[^>]+>")


def parse_page(path: Path, root: Path = WIKI) -> dict:
    raw = path.read_text(encoding="utf-8")
    meta = {}
    m = FRONT_RE.match(raw)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    rel = path.relative_to(root)
    if path == root / "index.md":
        title, category = HOME, "home"
    else:
        title = meta.get("title") or path.stem
        category = meta.get("category") or (rel.parts[0] if len(rel.parts) > 1 else "etc")
    return {
        "title": title,
        "category": category,
        "updated": meta.get("updated", ""),
        "order": int(meta.get("order", "1") or 1),
        "body": raw,
    }


def render(body: str, titles: set) -> str:
    def repl(m: re.Match) -> str:
        name = m.group(1).strip()
        esc = html.escape(name)
        if name in titles:
            return '<a class="wl" href="#" data-page="%s">%s</a>' % (esc, esc)
        return '<span class="wl missing" title="아직 없는 페이지">%s</span>' % esc

    body = LINK_RE.sub(repl, body)
    return markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])


def build(src: Path, out: Path, categories: list, site: str) -> int:
    """src 폴더의 md 전체를 out HTML 하나로 만든다. 업무 위키·공부 위키가 함께 쓴다."""
    files = sorted(p for p in src.rglob("*.md") if "_meta" not in p.relative_to(src).parts)
    pages = [parse_page(p, src) for p in files]
    titles = {p["title"] for p in pages}

    data = []
    for p in pages:
        body_html = render(p["body"], titles)
        # 본문 첫 제목(# ...)은 페이지 머리글과 겹치므로 뺀다
        body_html = re.sub(r"\A\s*<h1>.*?</h1>\s*", "", body_html, count=1, flags=re.S)
        text = html.unescape(TAG_RE.sub(" ", body_html))
        data.append({
            "title": p["title"],
            "category": p["category"],
            "updated": p["updated"],
            "order": p["order"],
            "html": body_html,
            "text": re.sub(r"\s+", " ", text).strip(),
        })

    payload = json.dumps(
        {"pages": data, "categories": categories, "home": HOME, "site": site,
         "built": datetime.now().strftime("%Y-%m-%d %H:%M")},
        ensure_ascii=False,
    ).replace("</", "<\\/")

    out.parent.mkdir(parents=True, exist_ok=True)
    html_text = TEMPLATE.replace("__SITE__", html.escape(site)).replace("__DATA__", payload)
    out.write_text(html_text, encoding="utf-8")
    count = sum(1 for p in pages if p["category"] != "home")
    print("%s 빌드 완료: 페이지 %d개 → %s" % (site, count, out.relative_to(ROOT)))
    return count


def main() -> None:
    build(WIKI, OUT, CATEGORIES, "업무 위키")

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_home
    build_home.main()


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__SITE__</title>
<style>
:root {
  --bg: #fafaf8; --panel: #f1f0ec; --text: #1f1f1d; --muted: #6b6a66;
  --line: #dddbd4; --accent: #2f5fb3; --accent-bg: #e6edf9; --missing: #a3a19b;
  --mark: #fff1a8;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1b1b1a; --panel: #242422; --text: #e9e7e2; --muted: #a09d96;
    --line: #3a3936; --accent: #8db1f0; --accent-bg: #2a3448; --missing: #6d6b66;
    --mark: #5a4d14;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; }
body {
  background: var(--bg); color: var(--text);
  font: 15px/1.65 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  display: grid; grid-template-columns: 260px 1fr; grid-template-rows: auto 1fr;
}
header {
  grid-column: 1 / -1; display: flex; gap: 16px; align-items: center;
  padding: 12px 20px; border-bottom: 1px solid var(--line); background: var(--panel);
}
#hub { color: var(--muted); text-decoration: none; font-size: 13px; white-space: nowrap; }
#hub:hover { color: var(--accent); }
header h1 { font-size: 17px; margin: 0; white-space: nowrap; cursor: pointer; }
#q {
  flex: 1; max-width: 420px; padding: 7px 12px; font: inherit; color: var(--text);
  background: var(--bg); border: 1px solid var(--line); border-radius: 8px;
}
#q:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
#built { color: var(--muted); font-size: 12px; margin-left: auto; white-space: nowrap; }
nav {
  overflow-y: auto; padding: 12px 10px 40px; border-right: 1px solid var(--line); background: var(--panel);
}
nav h2 {
  font-size: 12px; color: var(--muted); margin: 16px 10px 4px; font-weight: 600; letter-spacing: .02em;
}
nav a {
  display: block; padding: 4px 10px; border-radius: 6px; color: var(--text);
  text-decoration: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
nav a:hover { background: var(--line); }
nav a.on { background: var(--accent-bg); color: var(--accent); font-weight: 600; }
nav .hit { display: block; font-size: 12px; color: var(--muted); white-space: normal; }
nav .empty { padding: 8px 10px; color: var(--muted); }
main { overflow-y: auto; padding: 28px 40px 80px; }
article { max-width: 760px; }
article h1.title { font-size: 26px; margin: 0 0 4px; }
.meta { color: var(--muted); font-size: 13px; margin-bottom: 24px; }
article h2 { font-size: 18px; margin: 28px 0 8px; padding-bottom: 4px; border-bottom: 1px solid var(--line); }
article table { border-collapse: collapse; margin: 12px 0; }
article th, article td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; }
article th { background: var(--panel); }
article code { background: var(--panel); padding: 1px 5px; border-radius: 4px; }
article a { color: var(--accent); }
a.wl { text-decoration: none; border-bottom: 1px solid currentColor; cursor: pointer; }
.wl.missing { color: var(--missing); border-bottom: 1px dashed var(--missing); cursor: help; }
mark { background: var(--mark); color: inherit; }
@media (max-width: 720px) {
  body { grid-template-columns: 1fr; grid-template-rows: auto auto 1fr; }
  #built { display: none; }
  nav { max-height: 34vh; border-right: 0; border-bottom: 1px solid var(--line); }
  main { padding: 20px 16px 60px; }
}
</style>
</head>
<body>
<header>
  <a id="hub" href="../index.html" title="업무허브 홈">← 홈</a>
  <h1 id="home">__SITE__</h1>
  <input id="q" type="search" placeholder="제목·본문 검색" autocomplete="off">
  <span id="built"></span>
</header>
<nav id="nav"></nav>
<main><article id="doc"></article></main>
<script>
var DATA = __DATA__;
var byTitle = {};
DATA.pages.forEach(function (p) { byTitle[p.title] = p; });
var current = DATA.home;
var nav = document.getElementById("nav");
var doc = document.getElementById("doc");
var q = document.getElementById("q");
document.getElementById("built").textContent = "빌드 " + DATA.built;

function esc(s) {
  return s.replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
  });
}

function link(p, extra) {
  return '<a href="#" data-page="' + esc(p.title) + '"' + (p.title === current ? ' class="on"' : "") +
    ">" + esc(p.title) + (extra || "") + "</a>";
}

function snippet(text, term) {
  var i = text.toLowerCase().indexOf(term);
  if (i < 0) return "";
  var s = Math.max(0, i - 18), e = Math.min(text.length, i + term.length + 30);
  var part = text.slice(s, e);
  var j = i - s;
  return '<span class="hit">' + (s > 0 ? "…" : "") + esc(part.slice(0, j)) + "<mark>" +
    esc(part.slice(j, j + term.length)) + "</mark>" + esc(part.slice(j + term.length)) +
    (e < text.length ? "…" : "") + "</span>";
}

function drawNav() {
  var term = q.value.trim().toLowerCase();
  var out = "";
  if (!term) out += link(byTitle[DATA.home]);
  var groups = DATA.categories.slice();
  var known = {};
  groups.forEach(function (g) { known[g[0]] = true; });
  DATA.pages.forEach(function (p) {
    if (p.category !== "home" && !known[p.category]) { known[p.category] = true; groups.push([p.category, p.category]); }
  });
  var total = 0;
  groups.forEach(function (g) {
    var list = DATA.pages.filter(function (p) {
      if (p.category !== g[0]) return false;
      if (!term) return true;
      return p.title.toLowerCase().indexOf(term) >= 0 || p.text.toLowerCase().indexOf(term) >= 0;
    });
    if (g[0] === "journal") list.sort(function (a, b) { return a.title < b.title ? 1 : -1; });
    else list.sort(function (a, b) { return (a.order - b.order) || a.title.localeCompare(b.title, "ko"); });
    if (!list.length) return;
    total += list.length;
    out += "<h2>" + esc(g[1]) + " (" + list.length + ")</h2>";
    list.forEach(function (p) {
      var extra = term && p.title.toLowerCase().indexOf(term) < 0 ? snippet(p.text, term) : "";
      out += link(p, extra);
    });
  });
  if (term && !total) out = '<div class="empty">"' + esc(q.value.trim()) + '" 검색 결과 없음</div>';
  nav.innerHTML = out;
}

function show(title, push) {
  var p = byTitle[title];
  if (!p) return;
  current = title;
  var meta = p.updated ? "최종 수정 " + esc(p.updated) : "";
  doc.innerHTML = '<h1 class="title">' + esc(p.title) + "</h1>" +
    '<div class="meta">' + meta + "</div>" + p.html;
  drawNav();
  document.querySelector("main").scrollTop = 0;
  document.title = p.title + " - " + DATA.site;
  if (push !== false) history.replaceState(null, "", "#" + encodeURIComponent(title));
}

document.addEventListener("click", function (e) {
  var a = e.target.closest("a[data-page]");
  if (!a) return;
  e.preventDefault();
  show(a.getAttribute("data-page"));
});
document.getElementById("home").addEventListener("click", function () { q.value = ""; show(DATA.home); });
q.addEventListener("input", drawNav);
q.addEventListener("keydown", function (e) {
  if (e.key === "Enter") { var a = nav.querySelector("a[data-page]"); if (a) show(a.getAttribute("data-page")); }
  if (e.key === "Escape") { q.value = ""; drawNav(); }
});

var start = decodeURIComponent(location.hash.slice(1));
show(byTitle[start] ? start : DATA.home, false);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
