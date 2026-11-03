import os
import time
from playwright.sync_api import sync_playwright

artifact_dir = r"C:\Users\brred\.gemini\antigravity\brain\3a0156f3-1933-4219-a97c-29b123b76009"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 420, "height": 880})
        
        # Navigate using domcontentloaded
        page.goto("http://127.0.0.1:5077", wait_until="domcontentloaded", timeout=15000)
        time.sleep(1.0)

        # 1. Test Math Calculation: 245 * 18
        page.fill("#androidSearchInput", "245 * 18")
        time.sleep(0.5)
        math_shot = os.path.join(artifact_dir, "zero_os_everything_math.png")
        page.screenshot(path=math_shot)
        print("Captured math screenshot:", math_shot, flush=True)

        # 2. Test Contact Search: Alex
        page.fill("#androidSearchInput", "Alex")
        time.sleep(0.5)
        contact_shot = os.path.join(artifact_dir, "zero_os_everything_contact.png")
        page.screenshot(path=contact_shot)
        print("Captured contact screenshot:", contact_shot, flush=True)

        # 3. Test Phone Number Auto-Detection: 5550192
        page.fill("#androidSearchInput", "5550192")
        time.sleep(0.5)
        phone_shot = os.path.join(artifact_dir, "zero_os_everything_phone.png")
        page.screenshot(path=phone_shot)
        print("Captured phone screenshot:", phone_shot, flush=True)

        # 4. Test Unit Conversion: 100 km to miles
        page.fill("#androidSearchInput", "100 km to miles")
        time.sleep(0.5)
        conv_shot = os.path.join(artifact_dir, "zero_os_everything_convert.png")
        page.screenshot(path=conv_shot)
        print("Captured conversion screenshot:", conv_shot, flush=True)

        browser.close()

if __name__ == "__main__":
    run()
