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
        ("国家/地区", country_label),
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
