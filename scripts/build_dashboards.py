"""대시보드 갱신: scripts/dashboards/*.py 를 전부 실행하고 output/dashboards/index.html 목록을 다시 만든다.

실행: python3 scripts/build_dashboards.py
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts" / "dashboards"
OUT_DIR = ROOT / "output" / "dashboards"


def run_all() -> int:
    failed = 0
    for script in sorted(SCRIPTS.glob("*.py")):
        r = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode == 0:
            print(r.stdout.strip() or "완료: %s" % script.name)
        else:
            failed += 1
            print("실패: %s\n%s" % (script.name, r.stderr.strip()))
    return failed


def build_index() -> int:
    items = []
    for f in sorted(OUT_DIR.glob("*.html")):
        if f.name == "index.html":
            continue
        head = f.read_text(encoding="utf-8", errors="ignore")[:4000]
        t = re.search(r"<title>(.*?)</title>", head, re.S)
        d = re.search(r'<meta name="description" content="(.*?)"', head)
        items.append((
            t.group(1).strip() if t else f.stem,
            d.group(1) if d else "",
            f.name,
            datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            f.stat().st_size / 1e6,
        ))
    rows = "".join(
        '<a class="item" href="%s"><div class="t">%s</div><div class="d">%s</div>'
        '<div class="m">%s · 갱신 %s · %.1fMB</div></a>' % (html.escape(n), t, d, html.escape(n), m, s)
        for t, d, n, m, s in items
    ) or '<p class="m">아직 대시보드가 없습니다.</p>'
    (OUT_DIR / "index.html").write_text(INDEX.format(rows=rows, n=len(items),
                                                     built=datetime.now().strftime("%Y-%m-%d %H:%M")),
                                        encoding="utf-8")
    return len(items)


INDEX = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>대시보드 목록</title>
<style>
:root {{ color-scheme: light; }}
body {{ margin: 0; background: #fafaf8; color: #1f1f1d;
  font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
.wrap {{ max-width: 760px; margin: 0 auto; padding: 32px 16px; }}
h1 {{ font-size: 24px; margin: 0 0 4px; }}
.m {{ color: #6b6a66; font-size: 13px; }}
.list {{ margin-top: 20px; display: grid; gap: 10px; }}
.item {{ display: block; padding: 14px 16px; background: #fff; border: 1px solid #dddbd4; border-radius: 12px;
  color: inherit; text-decoration: none; }}
.item:hover {{ border-color: #2f5fb3; }}
.t {{ font-weight: 700; font-size: 17px; color: #2f5fb3; }}
</style>
</head>
<body>
<div class="wrap">
<h1>대시보드 목록</h1>
<div class="m"><a href="../../index.html">← 업무허브 홈</a> · {n}개 · 목록 갱신 {built}</div>
<div class="list">{rows}</div>
</div>
</body>
</html>
"""

def build_root_index() -> None:
    """GitHub Pages 첫 화면(루트 index.html)을 위키·대시보드 메뉴로 갱신한다."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_home
    build_home.main()


if __name__ == "__main__":
    failed = run_all()
    n = build_index()
    print("대시보드 목록 갱신: %d개 → output/dashboards/index.html" % n)
    build_root_index()
    sys.exit(1 if failed else 0)
