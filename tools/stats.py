import sqlite3


c = sqlite3.connect(r"C:\Users\Lenovo\pro2\parser\data\gan.db")
c.row_factory = sqlite3.Row


def rows(sql, params=()):
    return [dict(r) for r in c.execute(sql, params).fetchall()]


for country in ["au", "br"]:
    print("===", country)
    print("regions", rows("select region, count(*) n from company where country=? and status='published' and entity_type='dealer_store' group by region order by n desc", (country,)))
    print("brands", rows("""
        select b.name_zh, b.name_en, count(*) n
        from brand_representation br
        join company co on co.id=br.company_id
        join brand b on b.id=br.brand_id
        where co.country=? and co.status='published' and br.status='published' and br.is_current=1
        group by b.id order by n desc
    """, (country,)))
    print("groups", rows("""
        select p.name_local, count(*) n
        from corporate_link cl join company p on p.id=cl.parent_id
        where p.country=? and cl.status='published' group by p.id order by n desc limit 10
    """, (country,)))

print("=== jp signals")
print(rows("select signal_type, count(*) n from signal where country='jp' and status='published' group by 1 order by n desc"))
print("sources", rows("select source_id, count(*) n from signal where country='jp' and status='published' group by 1"))
