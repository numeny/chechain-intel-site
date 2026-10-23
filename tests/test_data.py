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
