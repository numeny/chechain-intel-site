from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .data import load_brand_relations, load_companies, load_group_links, load_signals
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
    out_dir = Path(args.out)
    if args.kind == "sample":
        out_dir = out_dir / "sample"
    out_dir.mkdir(parents=True, exist_ok=True)

    if country == "jp":
        signals = load_signals(db, country)
        path = out_dir / f"{slug}_signals_{generated_at}.pdf"
        write_signal_report(signals, path, label, generated_at)
        print(path)
        return 0

    all_rows = load_companies(db, country)
    all_relations = load_brand_relations(db, country)
    all_links = load_group_links(db, country)
    rows, relations, links = all_rows, all_relations, all_links
    cta = None
    if args.kind == "sample":
        rows = sample_rows(all_rows)
        allowed = {r.company_id for r in rows}
        names = {r.name for r in rows}
        relations = [r for r in all_relations if r.company_id in allowed]
        links = [r for r in all_links if r.parent_name in names and r.child_name in names]
        cta = (
            f"完整版：{len(all_rows)} 家企业、{len(all_relations)} 条品牌代理，499 元；"
            f"闲鱼搜索“{label}汽车经销商渠道地图”，或私信“样本”。"
        )
    xlsx = write_workbook(
        rows, out_dir / f"{slug}_dealers_{generated_at}.xlsx", label, generated_at,
        relations=relations, links=links, cta=cta,
    )
    pdf = write_country_report(
        rows, out_dir / f"{slug}_dealers_{generated_at}.pdf", label, generated_at, cta=cta,
    )
    print(xlsx)
    print(pdf)
    return 0
