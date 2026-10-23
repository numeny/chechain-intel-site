import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from export_intel.data import load_companies  # noqa: E402
from export_intel.sample import redact_url  # noqa: E402

DB = ROOT.parent / "parser" / "data" / "gan.db"
OUT = ROOT / "site" / "data" / "demo-data.js"

TYPE_LABELS = {"dealer_group": "经销商集团", "dealer_store": "经销商门店"}
COUNTRY_LABELS = {"au": "澳洲", "br": "巴西"}


def pick(rows, brand, limit):
    return [r for r in rows if brand in r.brands][:limit]


def main():
    demo = []
    for country, brands in [("au", ["比亚迪", "名爵"]), ("br", ["比亚迪", "奇瑞"])]:
        rows = load_companies(DB, country)
        picked = []
        for brand in brands:
            picked.extend(pick(rows, brand, 10))
        seen = set()
        for r in picked:
            if r.company_id in seen:
                continue
            seen.add(r.company_id)
            demo.append({
                "country": country,
                "country_label": COUNTRY_LABELS[country],
                "name": r.name,
                "type": TYPE_LABELS.get(r.entity_type, r.entity_type),
                "city": r.city,
                "region": r.region,
                "brands": r.brands,
                "group": r.group,
                "source_url": redact_url(r.source_url),
                "confidence": r.confidence,
                "updated_at": r.updated_at,
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "window.DEMO_DATA = " + json.dumps(demo, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"wrote {len(demo)} rows to {OUT}")


if __name__ == "__main__":
    main()
