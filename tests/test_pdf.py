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
    assert path.stat().st_size > 1000
