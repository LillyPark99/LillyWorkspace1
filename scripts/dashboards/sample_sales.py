"""data/raw/sample_sales.xlsx → output/dashboards/sample_sales.html

실행: python3 scripts/dashboards/sample_sales.py
- 데이터 파일만 바꾸고 다시 실행하면 숫자·차트가 갱신된다.
- plotly 라이브러리를 HTML 안에 넣어서(include_plotlyjs=True) 인터넷 없이 열린다.
- Python 3.9에서 동작하도록 작성했다.
"""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "raw" / "sample_sales.xlsx"
OUT = ROOT / "output" / "dashboards" / "sample_sales.html"
TITLE = "판매 대시보드"
DESC = "가상 판매 데이터: 월별 매출 추이, 품목·거래처 비중"

ACCENT = "#2f5fb3"
FONT = '-apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif'


def won(v: float) -> str:
    """금액을 읽기 쉬운 단위로 (억/만 원)."""
    if abs(v) >= 1e8:
        return "%.2f억 원" % (v / 1e8)
    return "{:,.0f}만 원".format(v / 1e4)


def style(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=10, r=20, t=10, b=10),
        font=dict(family=FONT, size=13, color="#1f1f1d"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(font_family=FONT), showlegend=False,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e6e4de")
    return fig


def main() -> None:
    df = pd.read_excel(SRC, sheet_name=0)
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["월"] = df["날짜"].dt.to_period("M")
    last_day = df["날짜"].max()

    monthly = df.groupby("월").agg(건수=("금액", "size"), 수량=("수량", "sum"), 매출=("금액", "sum")).reset_index()
    monthly["월표시"] = [("%d월" % m.month) if i and m.month != 1 else "%d년 %d월" % (m.year, m.month)
                     for i, m in enumerate(monthly["월"])]
    monthly["억"] = monthly["매출"] / 1e8

    # 마지막 달이 아직 안 끝났으면(말일 데이터가 없으면) 진행 중인 달로 표시
    last_month = monthly["월"].iloc[-1]
    partial = last_day.date() < last_month.end_time.date()
    done = monthly.iloc[:-1] if partial and len(monthly) > 1 else monthly

    # ---- 핵심 숫자 카드 ----
    total = df["금액"].sum()
    cur, prev = done.iloc[-1], (done.iloc[-2] if len(done) > 1 else None)
    change = (cur["매출"] / prev["매출"] - 1) * 100 if prev is not None else None
    top_client = df.groupby("거래처")["금액"].sum().sort_values(ascending=False)
    top_product = df.groupby("품목")["금액"].sum().sort_values(ascending=False)
    cards = [
        ("총매출", won(total), "%s ~ %s" % (df["날짜"].min().strftime("%m/%d"), last_day.strftime("%m/%d"))),
        ("%d월 매출" % cur["월"].month, won(cur["매출"]),
         ("전월 대비 %+.1f%%" % change) if change is not None else "비교할 전월 없음",
         "up" if (change or 0) >= 0 else "down"),
        ("거래 건수", "{:,}건".format(len(df)), "월평균 {:,.0f}건".format(done["건수"].mean())),
        ("매출 1위 거래처", top_client.index[0], "%s · 전체의 %.0f%%" % (won(top_client.iloc[0]), top_client.iloc[0] / total * 100)),
    ]

    # ---- 차트 1: 월별 매출 추이 ----
    hover = ["%s<br>매출 %s<br>%d건" % (m, won(v), n) for m, v, n in zip(monthly["월표시"], monthly["매출"], monthly["건수"])]
    if partial:
        hover[-1] += "<br>(%s까지 진행 중)" % last_day.strftime("%m/%d")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=done["월표시"], y=done["억"], mode="lines+markers+text",
        line=dict(color=ACCENT, width=3), marker=dict(size=9),
        text=[won(v) for v in done["매출"]], textposition="top center",
        hovertext=hover[:len(done)], hoverinfo="text",
    ))
    if partial:
        fig1.add_trace(go.Scatter(
            x=monthly["월표시"].iloc[-2:], y=monthly["억"].iloc[-2:], mode="lines+markers+text",
            line=dict(color=ACCENT, width=2, dash="dot"), marker=dict(size=9, symbol="circle-open"),
            text=["", won(monthly["매출"].iloc[-1]) + "<br>(진행 중)"], textposition="bottom left",
            hovertext=hover[-2:], hoverinfo="text",
        ))
    style(fig1)
    fig1.update_yaxes(rangemode="tozero", ticksuffix="억", tickformat=".1f")
    fig1.update_xaxes(type="category")

    # ---- 차트 2: 품목별 매출 ----
    p = top_product.sort_values()
    fig2 = go.Figure(go.Bar(
        x=p.values, y=p.index, orientation="h", marker_color=ACCENT,
        text=["%s (%.0f%%)" % (won(v), v / total * 100) for v in p.values], textposition="auto",
        hovertemplate="%{y}<br>%{text}<extra></extra>",
    ))
    style(fig2, 300)
    fig2.update_xaxes(showticklabels=False, showgrid=False)

    # ---- 차트 3: 거래처별 매출 (상위 10) ----
    c = top_client.head(10).sort_values()
    fig3 = go.Figure(go.Bar(
        x=c.values, y=c.index, orientation="h", marker_color=ACCENT,
        text=["%s (%.0f%%)" % (won(v), v / total * 100) for v in c.values], textposition="auto",
        hovertemplate="%{y}<br>%{text}<extra></extra>",
    ))
    style(fig3, 380)
    fig3.update_xaxes(showticklabels=False, showgrid=False)

    charts = [
        pio.to_html(fig1, full_html=False, include_plotlyjs=True, config={"displayModeBar": False}),
        pio.to_html(fig2, full_html=False, include_plotlyjs=False, config={"displayModeBar": False}),
        pio.to_html(fig3, full_html=False, include_plotlyjs=False, config={"displayModeBar": False}),
    ]

    # ---- 요약 표: 월 × 품목 매출 ----
    pivot = df.pivot_table(index="월", columns="품목", values="금액", aggfunc="sum", fill_value=0)
    pivot = pivot[top_product.index]
    pivot["합계"] = pivot.sum(axis=1)
    head = "".join("<th>%s</th>" % html.escape(str(col)) for col in pivot.columns)
    body = ""
    for idx, row in pivot.iterrows():
        label = idx.strftime("%Y-%m") + (" *" if partial and idx == last_month else "")
        body += "<tr><th>%s</th>%s</tr>" % (label, "".join("<td>{:,.0f}</td>".format(v) for v in row.values))
    sums = pivot.sum()
    body += '<tr class="sum"><th>합계</th>%s</tr>' % "".join("<td>{:,.0f}</td>".format(v) for v in sums.values)
    note = ("* %s은 %s까지의 데이터입니다." % (last_month.strftime("%Y-%m"), last_day.strftime("%m/%d"))) if partial else ""

    card_html = ""
    for card in cards:
        label, value, sub = card[:3]
        cls = card[3] if len(card) > 3 else ""
        card_html += '<div class="card"><div class="lbl">%s</div><div class="val">%s</div><div class="sub %s">%s</div></div>' % (
            html.escape(label), html.escape(value), cls, html.escape(sub))

    page = TEMPLATE.format(
        title=html.escape(TITLE), desc=html.escape(DESC), src=html.escape(str(SRC.relative_to(ROOT))),
        built=datetime.now().strftime("%Y-%m-%d %H:%M"), rows="{:,}".format(len(df)),
        cards=card_html, c1=charts[0], c2=charts[1], c3=charts[2],
        cur_month="%d월" % cur["월"].month,
        thead=head, tbody=body, note=html.escape(note),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print("대시보드 생성: %s (%d행, %.1fMB)" % (OUT.relative_to(ROOT), len(df), OUT.stat().st_size / 1e6))


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
<style>
:root {{ color-scheme: light; --line: #dddbd4; --muted: #6b6a66; --accent: #2f5fb3; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #fafaf8; color: #1f1f1d;
  font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
.wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 20px 60px; }}
header {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px; margin-bottom: 20px; }}
h1 {{ font-size: 24px; margin: 0; }}
.meta {{ color: var(--muted); font-size: 13px; }}
.meta a {{ color: var(--accent); }}
.cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
.card, .panel {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; }}
.card {{ padding: 14px 16px; }}
.lbl {{ color: var(--muted); font-size: 13px; }}
.val {{ font-size: 24px; font-weight: 700; margin: 2px 0; font-variant-numeric: tabular-nums; }}
.sub {{ font-size: 13px; color: var(--muted); }}
.sub.up {{ color: #1d7a46; }} .sub.down {{ color: #b3261e; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.panel {{ padding: 14px 16px; margin-bottom: 12px; min-width: 0; }}
.panel h2 {{ font-size: 16px; margin: 0 0 6px; }}
.panel .hint {{ color: var(--muted); font-size: 12px; margin: -4px 0 6px; }}
.tablebox {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; font-variant-numeric: tabular-nums; }}
th, td {{ border-bottom: 1px solid var(--line); padding: 7px 10px; text-align: right; white-space: nowrap; }}
thead th {{ color: var(--muted); font-weight: 600; }}
tbody th {{ text-align: left; font-weight: 500; }}
thead th:first-child {{ text-align: left; }}
tr.sum th, tr.sum td {{ font-weight: 700; border-top: 2px solid var(--line); border-bottom: 0; }}
.note {{ color: var(--muted); font-size: 12px; margin-top: 8px; }}
@media (max-width: 800px) {{
  .cards {{ grid-template-columns: 1fr 1fr; }}
  .grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>{title}</h1>
  <span class="meta">데이터: {src} · {rows}행 · 빌드 {built} · <a href="index.html">대시보드 목록</a> · <a href="../../index.html">업무허브 홈</a></span>
</header>
<section class="cards">{cards}</section>
<section class="panel">
  <h2>월별 매출 추이</h2>
  <p class="hint">점에 마우스를 올리면 금액과 건수가 보입니다. 점선은 아직 끝나지 않은 달입니다.</p>
  {c1}
</section>
<section class="grid">
  <div class="panel"><h2>품목별 매출 비중</h2>{c2}</div>
  <div class="panel"><h2>거래처별 매출 (상위 10)</h2>{c3}</div>
</section>
<section class="panel">
  <h2>월별 · 품목별 매출 요약 (원)</h2>
  <div class="tablebox"><table><thead><tr><th>월</th>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>
  <div class="note">{note}</div>
</section>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
