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
