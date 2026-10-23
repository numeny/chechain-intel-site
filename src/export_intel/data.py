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


@dataclass(frozen=True)
class BrandRelationRow:
    company_id: int
    company_name: str
    brand: str
    relationship_type: str
    source_url: str
    confidence: float
    updated_at: str


@dataclass(frozen=True)
class GroupLinkRow:
    parent_name: str
    child_name: str
    link_type: str
    source_url: str
    confidence: float


TYPE_LABELS = {"dealer_group": "经销商集团", "dealer_store": "经销商门店"}
RELATIONSHIP_LABELS = {"official_dealer": "官方授权经销商"}
LINK_LABELS = {"group_member": "集团成员"}
SIGNAL_LABELS = {
    "new_dealership": "新经销店",
    "partnership": "合作",
    "expansion": "扩张",
    "hiring": "招聘",
    "auto_show": "车展",
    "policy": "政策",
    "pricing": "价格",
    "other": "其他",
}


def type_label(value: str) -> str:
    return TYPE_LABELS.get(value, value)


def relationship_label(value: str) -> str:
    return RELATIONSHIP_LABELS.get(value, value)


def link_label(value: str) -> str:
    return LINK_LABELS.get(value, value)


def signal_label(value: str) -> str:
    return SIGNAL_LABELS.get(value, value)


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


def _company_name(row: sqlite3.Row) -> str:
    return row["name_local"] or row["name_en"] or row["name_zh"] or ""


def load_brand_relations(db_path: str | Path, country: str) -> list[BrandRelationRow]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            select br.company_id, c.name_zh, c.name_en, c.name_local,
                   b.name_zh as brand_zh, b.name_en as brand_en, b.name_ja as brand_ja,
                   br.relationship_type, br.evidence_url, br.confidence, br.updated_at
            from brand_representation br
            join company c on c.id = br.company_id
            join brand b on b.id = br.brand_id
            where c.country=? and c.status='published'
              and br.status='published' and br.is_current=1 and b.status='published'
            order by c.name_local, brand_zh
            """,
            (country,),
        ).fetchall()
    finally:
        conn.close()
    result = []
    for r in rows:
        brand = r["brand_zh"] or r["brand_en"] or r["brand_ja"] or ""
        result.append(
            BrandRelationRow(
                company_id=r["company_id"],
                company_name=_company_name(r),
                brand=brand,
                relationship_type=r["relationship_type"] or "",
                source_url=r["evidence_url"] or "",
                confidence=float(r["confidence"] or 0),
                updated_at=(r["updated_at"] or "")[:10],
            )
        )
    return result


def load_group_links(db_path: str | Path, country: str) -> list[GroupLinkRow]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            select p.name_local as parent_name, c.name_local as child_name,
                   cl.link_type, cl.evidence_url, cl.confidence
            from corporate_link cl
            join company p on p.id = cl.parent_id
            join company c on c.id = cl.child_id
            where p.country=? and p.status='published' and c.status='published'
              and cl.status='published' and cl.link_type='group_member'
            order by p.name_local, c.name_local
            """,
            (country,),
        ).fetchall()
    finally:
        conn.close()
    return [
        GroupLinkRow(
            parent_name=r["parent_name"] or "",
            child_name=r["child_name"] or "",
            link_type=r["link_type"] or "",
            source_url=r["evidence_url"] or "",
            confidence=float(r["confidence"] or 0),
        )
        for r in rows
    ]


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
