"""저장소 첫 화면(index.html)을 메뉴 페이지로 만든다.

실행: python3 scripts/build_home.py
- 업무 위키(output/wiki.html)와 대시보드(output/dashboards/*.html)로 들어가는 메뉴를 만든다.
- build_wiki.py, build_dashboards.py 끝에서도 자동으로 불린다.
- 외부 자원을 쓰지 않는다. Python 3.9에서 동작한다.
"""
from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
WIKI_HTML = ROOT / "output" / "wiki.html"
DASH_DIR = ROOT / "output" / "dashboards"
OUT = ROOT / "index.html"

CATEGORY_LABELS = {
    "accounts": "계정·시스템", "work": "업무 절차", "people": "사람·담당자",
    "terms": "용어·약어", "projects": "프로젝트", "journal": "업무 일지",
}


def mtime(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if p.exists() else "-"


def wiki_summary() -> tuple:
    counts = {}
    for p in WIKI.rglob("*.md"):
        rel = p.relative_to(WIKI)
        if len(rel.parts) < 2 or rel.parts[0] == "_meta":
            continue
        counts[rel.parts[0]] = counts.get(rel.parts[0], 0) + 1
    chips = "".join(
        '<a class="chip" href="output/wiki.html">%s <b>%d</b></a>' % (html.escape(CATEGORY_LABELS.get(k, k)), n)
        for k, n in sorted(counts.items(), key=lambda kv: list(CATEGORY_LABELS).index(kv[0])
                           if kv[0] in CATEGORY_LABELS else 99)
    )
    return sum(counts.values()), chips


def dashboards() -> list:
    items = []
    for f in sorted(DASH_DIR.glob("*.html")):
        if f.name == "index.html":
            continue
        head = f.read_text(encoding="utf-8", errors="ignore")[:4000]
        t = re.search(r"<title>(.*?)</title>", head, re.S)
        d = re.search(r'<meta name="description" content="(.*?)"', head)
        items.append((t.group(1).strip() if t else f.stem, d.group(1) if d else "", f.name, mtime(f)))
    return items


def main() -> None:
    n_pages, chips = wiki_summary()
    dash = dashboards()
    dash_rows = "".join(
        '<a class="row" href="output/dashboards/%s"><span class="rt">%s</span>'
        '<span class="rd">%s</span><span class="rm">갱신 %s</span></a>'
        % (html.escape(n), t, d, m) for t, d, n, m in dash
    ) or '<p class="muted">아직 대시보드가 없습니다.</p>'

    page = TEMPLATE.format(
        n_pages=n_pages, chips=chips, wiki_built=mtime(WIKI_HTML),
        n_dash=len(dash), dash_rows=dash_rows,
        built=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    OUT.write_text(page, encoding="utf-8")
    print("첫 화면 메뉴 갱신: 업무 위키 %d쪽, 대시보드 %d개 → index.html" % (n_pages, len(dash)))


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>업무허브</title>
<meta name="description" content="업무 위키와 데이터 분석 메뉴">
<style>
:root {{
  --bg: #fafaf8; --panel: #ffffff; --text: #1f1f1d; --muted: #6b6a66;
  --line: #dddbd4; --accent: #2f5fb3; --accent-bg: #e6edf9;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #1b1b1a; --panel: #242422; --text: #e9e7e2; --muted: #a09d96;
    --line: #3a3936; --accent: #8db1f0; --accent-bg: #2a3448;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--bg); color: var(--text);
  font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
}}
.wrap {{ max-width: 880px; margin: 0 auto; padding: 48px 20px 64px; }}
h1 {{ font-size: 28px; margin: 0 0 4px; letter-spacing: -0.01em; }}
.muted {{ color: var(--muted); font-size: 13px; }}
.sep {{ font-size: 13px; color: var(--muted); font-weight: 600; margin: 32px 0 0; letter-spacing: .02em; }}
.menu {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-top: 12px; }}
.card {{
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
  padding: 22px 22px 18px; display: flex; flex-direction: column;
}}
.card h2 {{ font-size: 20px; margin: 0; }}
.card p {{ margin: 6px 0 14px; color: var(--muted); }}
.open {{
  align-self: flex-start; margin-top: auto; padding: 8px 16px; border-radius: 8px;
  background: var(--accent); color: var(--bg); text-decoration: none; font-weight: 600;
}}
.open:hover {{ opacity: .9; }}
.stat {{ font-size: 13px; color: var(--muted); margin-bottom: 12px; }}
.stat b {{ color: var(--text); }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }}
.chip {{
  font-size: 13px; padding: 3px 10px; border-radius: 999px; text-decoration: none;
  background: var(--accent-bg); color: var(--accent);
}}
.rows {{ display: grid; gap: 8px; margin-bottom: 18px; }}
.row {{
  display: grid; gap: 2px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px;
  color: inherit; text-decoration: none;
}}
.row:hover, .card:hover .open {{ border-color: var(--accent); }}
.rt {{ font-weight: 600; color: var(--accent); }}
.rd {{ font-size: 13px; }}
.rm {{ font-size: 12px; color: var(--muted); }}
</style>
</head>
<body>
<div class="wrap">
<h1>업무허브</h1>
<div class="muted">메뉴를 골라 들어가세요 · 메뉴 갱신 {built}</div>

<h2 class="sep">업무</h2>
<div class="menu">
  <section class="card">
    <h2>업무 위키</h2>
    <p>메모·메일·대화에서 모은 업무 지식</p>
    <div class="stat">페이지 <b>{n_pages}</b>개 · 빌드 {wiki_built}</div>
    <div class="chips">{chips}</div>
    <a class="open" href="output/wiki.html">위키 열기</a>
  </section>

  <section class="card">
    <h2>데이터 분석</h2>
    <p>data/ 의 엑셀·CSV로 만든 대시보드</p>
    <div class="stat">대시보드 <b>{n_dash}</b>개</div>
    <div class="rows">{dash_rows}</div>
    <a class="open" href="output/dashboards/index.html">대시보드 목록</a>
  </section>
</div>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
