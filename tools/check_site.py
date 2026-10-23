from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "site" / "index.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors: list[str] = []
    failed: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("requestfailed", lambda req: failed.append(req.url))
    page.goto(URL, wait_until="networkidle")

    missing_anchors = page.evaluate(
        """() => [...document.querySelectorAll('a[href^="#"]')]
            .map(a => a.getAttribute('href'))
            .filter(h => h && h.length > 1 && !document.querySelector(h))"""
    )
    broken_images = page.evaluate(
        """() => [...document.images]
            .filter(i => !i.complete || i.naturalWidth === 0)
            .map(i => i.src)"""
    )
    print("page errors:", errors)
    print("failed requests:", failed)
    print("missing anchors:", missing_anchors)
    print("broken images:", broken_images)

    mobile = browser.new_page(viewport={"width": 390, "height": 844})
    mobile.goto(URL, wait_until="networkidle")
    mobile.click("#menuBtn")
    mobile.screenshot(path=str(ROOT / "site" / "preview-mobile-menu.png"))
    print("mobile menu open:", mobile.locator("#navLinks").evaluate("el => el.classList.contains('open')"))
    browser.close()
