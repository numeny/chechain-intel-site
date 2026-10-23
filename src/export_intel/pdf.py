from __future__ import annotations

from collections import Counter
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .data import CompanyRow, SignalRow

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

CN = "STSong-Light"
JP = "HeiseiKakuGo-W5"
TITLE = ParagraphStyle("title", fontName=CN, fontSize=18, leading=26, spaceAfter=8)
BODY = ParagraphStyle("body", fontName=CN, fontSize=9, leading=14)
CELL = ParagraphStyle("cell", fontName=CN, fontSize=8, leading=11)
HEAD = ParagraphStyle("head", fontName=CN, fontSize=8, leading=11, textColor=colors.white)
JP_CELL = ParagraphStyle("jp", fontName=JP, fontSize=8, leading=11)


def _p(text: str, style=BODY) -> Paragraph:
    safe = str(text or "").replace("&", "&amp;").replace("<", "&lt;")
    return Paragraph(safe, style)


def _table(data, widths):
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B0B0B0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
    ]))
    return table


def _distribution(values: list[str]) -> str:
    return "；".join(f"{k} {v}" for k, v in Counter(values).most_common()) or "无"


def write_country_report(rows: list[CompanyRow], path: str | Path, country_label: str, generated_at: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
    )
    type_labels = ["经销商集团" if r.entity_type == "dealer_group" else "经销商门店" for r in rows]
    brands = [b for r in rows for b in r.brands.split("、") if b]
    story = [
        Paragraph(f"{country_label}经销商与代理关系包", TITLE),
        _p(f"生成日期：{generated_at}　样本量：{len(rows)} 家企业"),
        Spacer(1, 6 * mm),
        _p("覆盖统计"),
        _p("类型分布：" + _distribution(type_labels)),
        _p("品牌分布：" + _distribution(brands)),
        Spacer(1, 4 * mm),
        _p("字段说明：企业名称、类型、城市/州、地址、代理品牌、所属集团、来源链接、置信度、更新时间。本报告不含联系方式。"),
        _p("合规声明：仅整理公开来源的企业级信息，不含个人信息；如信息有误，可凭来源链接申请更正或删除。"),
        Spacer(1, 4 * mm),
        _p("样本（前 20 条）"),
    ]
    data = [[
        _p("企业名称", HEAD), _p("类型", HEAD), _p("城市/州", HEAD),
        _p("代理品牌", HEAD), _p("所属集团", HEAD), _p("来源", HEAD),
    ]]
    for r in rows[:20]:
        data.append([
            _p(r.name, CELL), _p(r.entity_type, CELL), _p(f"{r.city} {r.region}".strip(), CELL),
            _p(r.brands, CELL), _p(r.group, CELL), _p(r.source_url[:60], CELL),
        ])
    story.append(_table(data, [42 * mm, 22 * mm, 28 * mm, 28 * mm, 30 * mm, 30 * mm]))
    doc.build(story)
    return path


def write_signal_report(signals: list[SignalRow], path: str | Path, country_label: str, generated_at: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
    )
    story = [
        Paragraph(f"{country_label}市场信号简报", TITLE),
        _p(f"生成日期：{generated_at}　信号数：{len(signals)} 条"),
        _p("信号类型分布：" + _distribution([s.signal_type for s in signals])),
        _p("合规声明：仅整理公开新闻与公告，不含个人信息；链接指向原始来源。"),
        Spacer(1, 3 * mm),
    ]
    data = [[_p("日期", HEAD), _p("类型", HEAD), _p("标题", HEAD), _p("来源", HEAD)]]
    for s in signals:
        data.append([
            _p(s.published_at, CELL), _p(s.signal_type, CELL),
            _p(s.title, JP_CELL), _p(s.url[:50], CELL),
        ])
    story.append(_table(data, [22 * mm, 22 * mm, 100 * mm, 36 * mm]))
    doc.build(story)
    return path
