from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "site" / "index.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=1)
    page.goto(URL, wait_until="networkidle")
    for selector, name in [
        ("#why", "why"),
        ("#coverage", "coverage"),
        ("#inside", "inside"),
        ("#sample", "sample"),
        ("#pricing", "pricing"),
        ("#custom", "custom"),
        ("#faq", "faq"),
        ("#contact", "contact"),
    ]:
        page.locator(selector).screenshot(path=str(ROOT / "site" / f"preview-{name}.png"))
        print(name)

    mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    mobile.goto(URL, wait_until="networkidle")
    mobile.screenshot(path=str(ROOT / "site" / "preview-mobile-top.png"))
    mobile.locator("#pricing").screenshot(path=str(ROOT / "site" / "preview-mobile-pricing.png"))
    print("mobile")
    browser.close()
