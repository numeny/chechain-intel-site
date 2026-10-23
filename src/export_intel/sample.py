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
