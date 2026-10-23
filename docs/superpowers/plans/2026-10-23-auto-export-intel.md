# 汽车出海情报变现实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 30 天内产出可售的澳洲/巴西经销商线索包与日本信号简报，并完成闲鱼/猪八戒/知乎上架素材。

**Architecture:** 在 `new_day` 建立独立、只读的导出工具，读取 `..\parser\data\gan.db`，生成 Excel/PDF/样本包；销售文案与交付模板独立放在 `sales/`，不修改 `parser` 代码。

**Tech Stack:** Python 3.11、openpyxl、reportlab、pytest。

## Global Constraints

- 只读访问 `C:\Users\Lenovo\pro2\parser\data\gan.db`，不写入、不修改 `parser`。
- 只导出 `company.status='published'`、`brand_representation.status='published'`、`signal.status='published'` 的记录。
- 标准包不含联系方式；不采集、不售卖个人信息。
- 所有对外材料标注来源与抓取日期，提供删除/更正通道。
- 不做冷邮件、不批量加微信、不投付费广告。
- 文件名使用英文；报告内标题与字段使用中文。

## File Structure

```
new_day/
├── pyproject.toml
├── .gitignore
├── src/export_intel/
│   ├── __init__.py
│   ├── data.py          # 只读查询、数据模型
│   ├── excel.py         # Excel 生成
│   ├── pdf.py           # PDF 生成
│   ├── sample.py        # 样本脱敏
│   └── cli.py           # 命令行入口
├── tools/export.py      # 薄封装，调用 cli.main
├── tests/
│   ├── conftest.py      # 临时 SQLite fixture
│   ├── test_data.py
│   ├── test_excel.py
│   ├── test_pdf.py
│   └── test_cli.py
├── deliverables/        # 生成物，gitignore
└── sales/
    ├── listings/
    ├── articles/
    └── templates/
```

---

### Task 1: 项目脚手架与数据层

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/export_intel/__init__.py`
- Create: `src/export_intel/data.py`
- Create: `tests/conftest.py`
- Create: `tests/test_data.py`

**Interfaces:**
- Produces: `CompanyRow`, `SignalRow`, `load_companies(db_path, country) -> list[CompanyRow]`, `load_signals(db_path, country) -> list[SignalRow]`。

- [ ] **Step 1: 创建虚拟环境并安装依赖**

Run:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install openpyxl reportlab pytest
```

- [ ] **Step 2: 写 `pyproject.toml`**

```toml
[project]
name = "export-intel"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["openpyxl>=3.1", "reportlab>=4.1"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
pythonpath = ["src"]
```

- [ ] **Step 3: 写 `.gitignore`**

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
deliverables/
```

- [ ] **Step 4: 写失败测试 `tests/conftest.py`**

```python
import sqlite3
import pytest


SCHEMA = """
create table company (
  id integer primary key, entity_type text, name_zh text, name_en text,
  name_local text, city text, region text, address_local text, website text,
  phone text, status text, confidence real, updated_at text, country text
);
create table brand (
  id integer primary key, name_zh text, name_en text, name_ja text, status text
);
create table brand_representation (
  id integer primary key, company_id integer, brand_id integer,
  relationship_type text, is_current integer, evidence_url text,
  status text, confidence real, updated_at text
);
create table corporate_link (
  id integer primary key, parent_id integer, child_id integer, link_type text,
  evidence_url text, status text, confidence real
);
create table signal (
  id integer primary key, signal_type text, title_original text, title_zh text,
  summary_original text, summary_zh text, url text, published_at text,
  status text, country text
);
"""


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "gan.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.executemany(
        "insert into company values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (1, "dealer_group", None, None, "Autosports Group", None, None, None, None, None, "published", 0.8, "2026-10-16T10:00:00+00:00", "au"),
            (2, "dealer_store", None, None, "BYD Sydney", "Sydney", "NSW", "1 George St, Sydney NSW 2000", None, None, "published", 0.9, "2026-10-17T10:00:00+00:00", "au"),
            (3, "dealer_store", None, None, "MG Melbourne", "Melbourne", "VIC", "2 Queen St, Melbourne VIC 3000", None, None, "published", 0.7, "2026-10-18T10:00:00+00:00", "au"),
            (4, "dealer_store", None, None, "BYD Carpina", "Carpina", "PE", "BR-408, Carpina, PE", None, None, "published", 0.8, "2026-10-19T10:00:00+00:00", "br"),
            (5, "dealer_store", None, None, "Pending Motors", "Perth", "WA", "3 St Georges Tce", None, None, "pending_review", 0.5, "2026-10-20T10:00:00+00:00", "au"),
        ],
    )
    conn.executemany(
        "insert into brand values (?,?,?,?,?)",
        [(1, "比亚迪", "BYD", "BYD", "published"), (2, "名爵", "MG", "MG", "published")],
    )
    conn.executemany(
        "insert into brand_representation values (?,?,?,?,?,?,?,?,?)",
        [
            (1, 2, 1, "official_dealer", 1, "https://bydsydney.example.com/?utm=x", "published", 0.9, "2026-10-17"),
            (2, 3, 2, "official_dealer", 1, "https://mgmelbourne.example.com/", "published", 0.8, "2026-10-18"),
            (3, 4, 1, "official_dealer", 1, "https://byd.example.com/api?country=BR", "published", 0.8, "2026-10-19"),
        ],
    )
    conn.executemany(
        "insert into corporate_link values (?,?,?,?,?,?,?)",
        [(1, 1, 2, "group_member", "https://autosports.example.com/", "published", 0.7)],
    )
    conn.executemany(
        "insert into signal values (?,?,?,?,?,?,?,?,?,?)",
        [
            (1, "expansion", "中国EVメーカーが新店舗", None, "新店舗を開設", None, "https://example.jp/1", "2026-10-18", "published", "jp"),
            (2, "policy", "未发布", None, None, None, "https://example.jp/2", "2026-10-19", "pending_review", "jp"),
        ],
    )
    conn.commit()
    conn.close()
    return path
```

- [ ] **Step 5: 写失败测试 `tests/test_data.py`**

```python
from export_intel.data import load_companies, load_signals


def test_load_companies_filters_published_and_aggregates(db_path):
    rows = load_companies(db_path, "au")
    assert [r.company_id for r in rows] == [1, 2, 3]
    by_id = {r.company_id: r for r in rows}
    assert by_id[2].name == "BYD Sydney"
    assert by_id[2].brands == "比亚迪"
    assert by_id[2].group == "Autosports Group"
    assert by_id[2].source_url == "https://bydsydney.example.com/?utm=x"
    assert by_id[1].source_url == "https://autosports.example.com/"


def test_load_companies_brazil(db_path):
    rows = load_companies(db_path, "br")
    assert len(rows) == 1
    assert rows[0].brands == "比亚迪"


def test_load_signals_filters_published(db_path):
    rows = load_signals(db_path, "jp")
    assert len(rows) == 1
    assert rows[0].title == "中国EVメーカーが新店舗"
    assert rows[0].signal_type == "expansion"
```

- [ ] **Step 6: 运行测试确认失败**

Run: `.venv\Scripts\python -m pytest tests/test_data.py -v`
Expected: FAIL，`ModuleNotFoundError: No module named 'export_intel'`。

- [ ] **Step 7: 实现 `src/export_intel/data.py`**

```python
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CompanyRow:
    company_id: int
    name: str
    entity_type: str
    country: str
    city: str
    region: str
    address: str
    brands: str
    group: str
    source_url: str
    confidence: float
    updated_at: str


@dataclass(frozen=True)
class SignalRow:
    signal_id: int
    signal_type: str
    title: str
    summary: str
    url: str
    published_at: str
    country: str


def _connect(db_path: str | Path) -> sqlite3.Connection:
    uri = f"file:{Path(db_path).as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _brand_name(row: sqlite3.Row) -> str:
    for key in ("name_zh", "name_en", "name_ja"):
        if row[key]:
            return row[key]
    return ""


def load_companies(db_path: str | Path, country: str) -> list[CompanyRow]:
    conn = _connect(db_path)
    try:
        companies = conn.execute(
            "select * from company where country=? and status='published' order by entity_type, name_local",
            (country,),
        ).fetchall()
        reps = conn.execute(
            """
            select br.company_id, b.name_zh, b.name_en, b.name_ja, br.evidence_url
            from brand_representation br
            join brand b on b.id = br.brand_id
            where br.status='published' and br.is_current=1 and b.status='published'
            """,
        ).fetchall()
        links = conn.execute(
            """
            select cl.parent_id, cl.child_id, cl.evidence_url, p.name_local as parent_name
            from corporate_link cl
            join company p on p.id = cl.parent_id
            where cl.status='published' and cl.link_type='group_member'
            """,
        ).fetchall()
    finally:
        conn.close()

    brands: dict[int, set[str]] = {}
    source: dict[int, str] = {}
    for r in reps:
        name = _brand_name(r)
        if name:
            brands.setdefault(r["company_id"], set()).add(name)
        if r["evidence_url"] and r["company_id"] not in source:
            source[r["company_id"]] = r["evidence_url"]

    group: dict[int, str] = {}
    for r in links:
        if r["parent_name"]:
            group[r["child_id"]] = r["parent_name"]
        if r["evidence_url"]:
            source.setdefault(r["child_id"], r["evidence_url"])
            source.setdefault(r["parent_id"], r["evidence_url"])

    result = []
    for c in companies:
        result.append(
            CompanyRow(
                company_id=c["id"],
                name=c["name_local"] or c["name_en"] or c["name_zh"] or "",
                entity_type=c["entity_type"] or "",
                country=c["country"] or "",
                city=c["city"] or "",
                region=c["region"] or "",
                address=c["address_local"] or "",
                brands="、".join(sorted(brands.get(c["id"], set()))),
                group=group.get(c["id"], ""),
                source_url=source.get(c["id"], "") or c["website"] or "",
                confidence=float(c["confidence"] or 0),
                updated_at=(c["updated_at"] or "")[:10],
            )
        )
    return result


def load_signals(db_path: str | Path, country: str) -> list[SignalRow]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            select id, signal_type, title_original, title_zh,
                   summary_original, summary_zh, url, published_at, country
            from signal
            where country=? and status='published'
            order by published_at desc, id desc
            """,
            (country,),
        ).fetchall()
    finally:
        conn.close()
    return [
        SignalRow(
            signal_id=r["id"],
            signal_type=r["signal_type"] or "",
            title=r["title_zh"] or r["title_original"] or "",
            summary=r["summary_zh"] or r["summary_original"] or "",
            url=r["url"] or "",
            published_at=(r["published_at"] or "")[:10],
            country=r["country"] or "",
        )
        for r in rows
    ]
```

- [ ] **Step 8: 运行测试确认通过**

Run: `.venv\Scripts\python -m pytest tests/test_data.py -v`
Expected: 3 passed。

- [ ] **Step 9: 提交**

```bash
git add pyproject.toml .gitignore src tests
git commit -m "feat: add published data reader for export tool"
```

---

### Task 2: Excel 生成

**Files:**
- Create: `src/export_intel/excel.py`
- Test: `tests/test_excel.py`

**Interfaces:**
- Consumes: `CompanyRow`。
- Produces: `write_workbook(rows, path, country_label, generated_at) -> Path`。

- [ ] **Step 1: 写失败测试 `tests/test_excel.py`**

```python
from openpyxl import load_workbook

from export_intel.data import CompanyRow
from export_intel.excel import write_workbook


def _row(**overrides):
    data = dict(
        company_id=2, name="BYD Sydney", entity_type="dealer_store",
        country="au", city="Sydney", region="NSW",
        address="1 George St", brands="比亚迪", group="Autosports Group",
        source_url="https://example.com", confidence=0.9,
        updated_at="2026-10-17",
    )
    data.update(overrides)
    return CompanyRow(**data)


def test_write_workbook_creates_expected_sheets(tmp_path):
    path = write_workbook([_row()], tmp_path / "au.xlsx", "澳洲", "2026-10-23")
    assert path.exists()
    wb = load_workbook(path)
    assert wb.sheetnames == ["企业", "说明"]
    ws = wb["企业"]
    assert ws["A1"].value == "企业ID"
    assert ws["B2"].value == "BYD Sydney"
    assert ws["H2"].value == "比亚迪"
    assert ws["I2"].value == "Autosports Group"
    assert ws["J2"].hyperlink.target == "https://example.com"
    assert wb["说明"]["B2"].value == "澳洲"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv\Scripts\python -m pytest tests/test_excel.py -v`
Expected: FAIL，`ModuleNotFoundError` 或 `cannot import name 'write_workbook'`。

- [ ] **Step 3: 实现 `src/export_intel/excel.py`**

```python
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .data import CompanyRow

HEADERS = ["企业ID", "企业名称", "类型", "国家", "城市", "州/省", "地址", "代理品牌", "所属集团", "来源链接", "置信度", "更新时间"]
WIDTHS = [8, 32, 14, 8, 16, 10, 40, 24, 28, 45, 10, 12]


def _type_label(value: str) -> str:
    return {"dealer_group": "经销商集团", "dealer_store": "经销商门店"}.get(value, value)


def write_workbook(rows: list[CompanyRow], path: str | Path, country_label: str, generated_at: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "企业"
    ws.append(HEADERS)
    for col, width in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(col)].width = width
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:L{max(len(rows) + 1, 1)}"

    for r in rows:
        ws.append([
            r.company_id, r.name, _type_label(r.entity_type), r.country.upper(),
            r.city, r.region, r.address, r.brands, r.group, r.source_url,
            r.confidence, r.updated_at,
        ])
        row = ws.max_row
        if r.source_url.startswith(("http://", "https://")):
            cell = ws.cell(row=row, column=10)
            cell.hyperlink = r.source_url
            cell.style = "Hyperlink"
        for col in (7, 10):
            ws.cell(row=row, column=col).alignment = Alignment(wrap_text=True, vertical="top")

    info = wb.create_sheet("说明")
    info.column_dimensions["A"].width = 18
    info.column_dimensions["B"].width = 80
    info_rows = [
        ("报告名称", f"{country_label}经销商与代理关系包"),
        ("生成日期", generated_at),
        ("数据口径", "仅包含已审核发布的公开来源记录；不含联系方式。"),
        ("字段说明", "代理品牌为该企业当前在售/代理品牌；所属集团来自公开集团关系。"),
        ("来源", "来源链接为公开网页或品牌方公开接口；抓取日期见各行更新时间。"),
        ("合规", "不含个人信息；如信息有误，可凭来源链接申请更正或删除。"),
        ("免责", "本报告为公开信息整理，不构成投资或交易建议；请以品牌方/企业官方信息为准。"),
    ]
    for row in info_rows:
        info.append(row)
    for cell in info["A"]:
        cell.font = Font(bold=True)

    wb.save(path)
    return path
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv\Scripts\python -m pytest tests/test_excel.py -v`
Expected: 1 passed。

- [ ] **Step 5: 提交**

```bash
git add src/export_intel/excel.py tests/test_excel.py
git commit -m "feat: add Excel exporter"
```

---

### Task 3: PDF 报告

**Files:**
- Create: `src/export_intel/pdf.py`
- Test: `tests/test_pdf.py`

**Interfaces:**
- Consumes: `CompanyRow`, `SignalRow`。
- Produces: `write_country_report(rows, path, country_label, generated_at) -> Path`、`write_signal_report(signals, path, country_label, generated_at) -> Path`。

- [ ] **Step 1: 写失败测试 `tests/test_pdf.py`**

```python
from export_intel.data import CompanyRow, SignalRow
from export_intel.pdf import write_country_report, write_signal_report


def test_write_country_report(tmp_path):
    row = CompanyRow(2, "BYD Sydney", "dealer_store", "au", "Sydney", "NSW",
                     "1 George St", "比亚迪", "Autosports Group",
                     "https://example.com", 0.9, "2026-10-17")
    path = write_country_report([row], tmp_path / "au.pdf", "澳洲", "2026-10-23")
    assert path.exists()
    assert path.read_bytes()[:4] == b"%PDF"
    assert path.stat().st_size > 1000


def test_write_signal_report(tmp_path):
    signal = SignalRow(1, "expansion", "中国EVメーカーが新店舗", "新店舗を開設",
                       "https://example.jp/1", "2026-10-18", "jp")
    path = write_signal_report([signal], tmp_path / "jp.pdf", "日本", "2026-10-23")
    assert path.exists()
    assert path.read_bytes()[:4] == b"%PDF"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv\Scripts\python -m pytest tests/test_pdf.py -v`
Expected: FAIL，`ModuleNotFoundError` 或 `cannot import name`。

- [ ] **Step 3: 实现 `src/export_intel/pdf.py`**

```python
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
JP_CELL = ParagraphStyle("jp", fontName=JP, fontSize=8, leading=11)


def _p(text: str, style=BODY) -> Paragraph:
    return Paragraph(str(text or "").replace("&", "&amp;").replace("<", "&lt;"), style)


def _table(data, widths):
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), CN),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B0B0B0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
    ]))
    return table


def write_country_report(rows: list[CompanyRow], path: str | Path, country_label: str, generated_at: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    story = [
        Paragraph(f"{country_label}经销商与代理关系包", TITLE),
        _p(f"生成日期：{generated_at}　样本量：{len(rows)} 家企业"),
        Spacer(1, 6 * mm),
        _p("覆盖统计"),
        _p("类型分布：" + "；".join(f"{k} {v}" for k, v in Counter({"经销商集团": sum(r.entity_type == "dealer_group" for r in rows), "经销商门店": sum(r.entity_type == "dealer_store" for r in rows)}).items())),
        _p("品牌分布：" + "；".join(f"{k} {v}" for k, v in Counter(b for r in rows for b in r.brands.split("、") if b).most_common(12))),
        Spacer(1, 4 * mm),
        _p("字段说明：企业名称、类型、城市/州、地址、代理品牌、所属集团、来源链接、置信度、更新时间。本报告不含联系方式。"),
        _p("合规声明：仅整理公开来源的企业级信息，不含个人信息；如信息有误，可凭来源链接申请更正或删除。"),
        Spacer(1, 4 * mm),
        _p("样本（前 20 条）"),
    ]
    data = [[_p("企业名称", CELL), _p("类型", CELL), _p("城市/州", CELL), _p("代理品牌", CELL), _p("所属集团", CELL), _p("来源", CELL)]]
    for r in rows[:20]:
        data.append([_p(r.name, CELL), _p(r.entity_type, CELL), _p(f"{r.city} {r.region}".strip(), CELL),
                     _p(r.brands, CELL), _p(r.group, CELL), _p(r.source_url[:60], CELL)])
    story.append(_table(data, [42 * mm, 22 * mm, 28 * mm, 28 * mm, 30 * mm, 30 * mm]))
    doc.build(story)
    return path


def write_signal_report(signals: list[SignalRow], path: str | Path, country_label: str, generated_at: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    story = [
        Paragraph(f"{country_label}市场信号简报", TITLE),
        _p(f"生成日期：{generated_at}　信号数：{len(signals)} 条"),
        _p("信号类型分布：" + "；".join(f"{k} {v}" for k, v in Counter(s.signal_type for s in signals).most_common())),
        _p("合规声明：仅整理公开新闻与公告，不含个人信息；链接指向原始来源。"),
        Spacer(1, 3 * mm),
    ]
    data = [[_p("日期", CELL), _p("类型", CELL), _p("标题", CELL), _p("来源", CELL)]]
    for s in signals:
        data.append([_p(s.published_at, CELL), _p(s.signal_type, CELL), _p(s.title, JP_CELL), _p(s.url[:50], CELL)])
    story.append(_table(data, [22 * mm, 22 * mm, 100 * mm, 36 * mm]))
    doc.build(story)
    return path
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv\Scripts\python -m pytest tests/test_pdf.py -v`
Expected: 2 passed。若中文/日文显示异常，改为 Edge headless HTML→PDF；先完成功能再优化字体。

- [ ] **Step 5: 提交**

```bash
git add src/export_intel/pdf.py tests/test_pdf.py
git commit -m "feat: add PDF reports"
```

---

### Task 4: 样本脱敏与 CLI

**Files:**
- Create: `src/export_intel/sample.py`
- Create: `src/export_intel/cli.py`
- Create: `tools/export.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `load_companies`, `load_signals`, `write_workbook`, `write_country_report`, `write_signal_report`。
- Produces: `sample_rows(rows, limit=10)`、`redact_address(value)`、`redact_url(value)`、`main(argv=None)`。

- [ ] **Step 1: 写失败测试 `tests/test_cli.py`**

```python
import re
from openpyxl import load_workbook

from export_intel.cli import main


def test_cli_generates_full_and_sample(db_path, tmp_path):
    out = tmp_path / "deliverables"
    assert main(["--db", str(db_path), "--country", "au", "--kind", "full", "--out", str(out)]) == 0
    files = list(out.rglob("*"))
    assert any(p.suffix == ".xlsx" for p in files)
    assert any(p.suffix == ".pdf" for p in files)

    sample = out / "sample"
    assert main(["--db", str(db_path), "--country", "au", "--kind", "sample", "--out", str(sample)]) == 0
    xlsx = next(sample.rglob("*.xlsx"))
    wb = load_workbook(xlsx)
    ws = wb["企业"]
    assert ws.max_row - 1 <= 10
    address = ws["G2"].value
    assert not re.search(r"\d", address or "")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv\Scripts\python -m pytest tests/test_cli.py -v`
Expected: FAIL，`ImportError`。

- [ ] **Step 3: 实现 `src/export_intel/sample.py`**

```python
from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

from .data import CompanyRow


def redact_address(value: str) -> str:
    value = re.sub(r"\d+[-\d/]*\s*", "", value or "")
    value = re.sub(r"\s{2,}", " ", value).strip(" ,")
    return value


def redact_url(value: str) -> str:
    if not value:
        return ""
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def sample_rows(rows: list[CompanyRow], limit: int = 10) -> list[CompanyRow]:
    groups = [r for r in rows if r.entity_type == "dealer_group"][:2]
    stores = [r for r in rows if r.entity_type != "dealer_group"]
    picked = groups + stores[: max(limit - len(groups), 0)]
    result = []
    for r in picked:
        result.append(
            CompanyRow(
                company_id=r.company_id, name=r.name, entity_type=r.entity_type,
                country=r.country, city=r.city, region=r.region,
                address=redact_address(r.address), brands=r.brands, group=r.group,
                source_url=redact_url(r.source_url), confidence=r.confidence,
                updated_at=r.updated_at,
            )
        )
    return result[:limit]
```

- [ ] **Step 4: 实现 `src/export_intel/cli.py`**

```python
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .data import load_companies, load_signals
from .excel import write_workbook
from .pdf import write_country_report, write_signal_report
from .sample import sample_rows

LABELS = {"au": "澳洲", "br": "巴西", "jp": "日本"}
SLUGS = {"au": "australia", "br": "brazil", "jp": "japan"}


def _default_db() -> Path:
    return Path(__file__).resolve().parents[2].parent / "parser" / "data" / "gan.db"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export automotive dealer intelligence")
    parser.add_argument("--db", default=str(_default_db()))
    parser.add_argument("--country", choices=["au", "br", "jp"], required=True)
    parser.add_argument("--kind", choices=["full", "sample"], default="full")
    parser.add_argument("--out", default="deliverables")
    args = parser.parse_args(argv)

    db = Path(args.db)
    if not db.exists():
        parser.error(f"database not found: {db}")

    country = args.country
    label = LABELS[country]
    slug = SLUGS[country]
    generated_at = date.today().isoformat()
    out_dir = Path(args.out) / ("sample" if args.kind == "sample" else "")
    out_dir.mkdir(parents=True, exist_ok=True)

    if country == "jp":
        signals = load_signals(db, country)
        path = out_dir / f"{slug}_signals_{generated_at}.pdf"
        write_signal_report(signals, path, label, generated_at)
        print(path)
        return 0

    rows = load_companies(db, country)
    if args.kind == "sample":
        rows = sample_rows(rows)
    xlsx = write_workbook(rows, out_dir / f"{slug}_dealers_{generated_at}.xlsx", label, generated_at)
    pdf = write_country_report(rows, out_dir / f"{slug}_dealers_{generated_at}.pdf", label, generated_at)
    print(xlsx)
    print(pdf)
    return 0
```

- [ ] **Step 5: 实现 `tools/export.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from export_intel.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: 运行测试确认通过**

Run: `.venv\Scripts\python -m pytest tests/test_cli.py -v`
Expected: 1 passed。

- [ ] **Step 7: 用真实数据库生成全部交付物**

Run:
```powershell
.venv\Scripts\python tools\export.py --country au --kind full
.venv\Scripts\python tools\export.py --country br --kind full
.venv\Scripts\python tools\export.py --country jp --kind full
.venv\Scripts\python tools\export.py --country au --kind sample
.venv\Scripts\python tools\export.py --country br --kind sample
```
Expected: `deliverables/` 下生成 5 个文件，AU/BR Excel 行数分别为 353/378。

- [ ] **Step 8: 提交**

```bash
git add src tests tools
git commit -m "feat: add sample redaction and export CLI"
```

---

### Task 5: 销售资产

**Files:**
- Create: `sales/listings/xianyu.md`
- Create: `sales/listings/zhubajie.md`
- Create: `sales/templates/faq.md`
- Create: `sales/templates/delivery.md`
- Create: `sales/articles/`（10 个 md 文件）

**Interfaces:**
- Consumes: 真实交付物中的数字（353/378/70）。
- Produces: 可直接复制到平台的上架文案与文章。

- [ ] **Step 1: 写闲鱼文案（3 条）**

`sales/listings/xianyu.md` 包含：
- 澳洲包：标题、价格 499、封面文案、详情（含字段、样本、交付方式、退款规则）。
- 巴西包：同上。
- 定制调研：3,000 元起，7 个工作日。
- 统一声明：不含联系方式；只整理公开信息；样本可先看。

- [ ] **Step 2: 写猪八戒文案**

`sales/listings/zhubajie.md`：服务标题、服务范围、交付周期、报价档位（3,000/4,500/6,000）、不接的范围（个人隐私、爬取非公开数据）。

- [ ] **Step 3: 写 FAQ 与交付模板**

`sales/templates/faq.md`：数据来源、更新频率、是否含联系方式、能否定制、退款规则、发票。
`sales/templates/delivery.md`：收款后 30 分钟内的交付话术、文件命名、验收确认、售后 7 天。

- [ ] **Step 4: 写 10 篇文章**

`sales/articles/` 下 10 个文件，每篇 800-1200 字，标题示例：
1. 澳洲汽车经销商集团名单怎么找？公开信息渠道汇总
2. 巴西汽车经销商开发：CNPJ、州与品牌代理关系
3. 中国汽配出海澳洲：先找经销商还是先找进口商？
4. 日本汽车市场信号：哪些公开信息值得跟踪？
5. 澳洲比亚迪/名爵门店分布说明了什么？
6. 巴西 BYD 门店扩张的公开信号
7. 海外经销商名单为什么容易过时？
8. 汽配出口商开发海外渠道的 5 个公开数据源
9. 如何验证海外经销商是否真的代理某个品牌
10. 海外市场调研报告应该包含哪些字段？

每篇文末引导：“需要三国经销商 Excel 样本，可在闲鱼搜索……或私信‘样本’。”

- [ ] **Step 5: 检查合规与数字一致性**

Run:
```powershell
Select-String -Path sales\**\*.md -Pattern "联系方式|邮箱|手机号" -SimpleMatch
```
Expected: 只出现在“不含联系方式/不采集个人信息”的否定语境。

- [ ] **Step 6: 提交**

```bash
git add sales
git commit -m "docs: add sales listings and content assets"
```

---

### Task 6: 端到端验收与交付手册

**Files:**
- Create: `sales/templates/delivery-runbook.md`
- Modify: `README.md`

- [ ] **Step 1: 跑完整测试**

Run: `.venv\Scripts\python -m pytest -v`
Expected: 全部通过。

- [ ] **Step 2: 校验真实交付物**

Run:
```powershell
.venv\Scripts\python -c "from openpyxl import load_workbook; wb=load_workbook('deliverables/australia_dealers_2026-10-23.xlsx'); print(wb['企业'].max_row-1); wb2=load_workbook('deliverables/brazil_dealers_2026-10-23.xlsx'); print(wb2['企业'].max_row-1)"
```
Expected: 353 和 378。

- [ ] **Step 3: 写交付手册**

`sales/templates/delivery-runbook.md`：
- 收款后流程（确认版本 → 发文件 → 30 分钟验收 → 7 天售后）。
- 文件命名与话术。
- 退款规则（未交付全退；已交付不退，可换版本）。
- 每周更新流程（运行 parser → 重新导出 → 通知订阅客户）。

- [ ] **Step 4: 更新 README**

写明项目目的、目录结构、生成命令、合规边界、30 天目标与止损规则。

- [ ] **Step 5: 提交**

```bash
git add README.md sales/templates/delivery-runbook.md
git commit -m "docs: add delivery runbook and project README"
```

---

## Self-Review

- **Spec coverage:** 产品/定价 → Task 2/3/4 + 销售资产 Task 5；合规 → Global Constraints + Task 5 Step 5；30 天计划 → 本计划外由用户执行上架与获客；技术实现 → Task 1-4；验收 → Task 6。
- **Placeholder scan:** 无 TBD/TODO；文章标题已列，正文由执行时撰写。
- **Type consistency:** `CompanyRow`/`SignalRow` 字段在 data/excel/pdf/sample/cli 中一致；`write_workbook`、`write_country_report`、`write_signal_report` 签名一致。
