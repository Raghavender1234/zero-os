import os
import time
from playwright.sync_api import sync_playwright

artifact_dir = r"C:\Users\brred\.gemini\antigravity\brain\3a0156f3-1933-4219-a97c-29b123b76009"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 420, "height": 880})
        page.goto("http://127.0.0.1:5077", wait_until="domcontentloaded")
        time.sleep(1.2)

        # 1. Type natural routine into Everything Bar
        page.fill("#androidSearchInput", "auto: at 11pm grayscale and silent")
        time.sleep(0.5)
        card_shot = os.path.join(artifact_dir, "zero_os_zeroflow_card.png")
        page.screenshot(path=card_shot)
        print("Captured ZeroFlow card screenshot:", card_shot, flush=True)

        # 2. Click Save Routine
        page.click(".tray-btn.primary")
        time.sleep(0.8)

        # 3. Open Settings to see the Active Routines view
        page.click("#icon-settings")
        time.sleep(0.8)
        settings_shot = os.path.join(artifact_dir, "zero_os_zeroflow_settings.png")
        page.screenshot(path=settings_shot)
        print("Captured ZeroFlow settings screenshot:", settings_shot, flush=True)

        browser.close()

if __name__ == "__main__":
    run()
