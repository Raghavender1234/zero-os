import os
import time
from playwright.sync_api import sync_playwright

artifact_dir = r"C:\Users\brred\.gemini\antigravity\brain\3a0156f3-1933-4219-a97c-29b123b76009"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 420, "height": 880})
        page.goto("http://127.0.0.1:5077", wait_until="domcontentloaded")
        time.sleep(1.0)

        # 1. Test Timer: timer 10 mins
        page.fill("#androidSearchInput", "timer 10 mins")
        time.sleep(0.5)
        timer_shot = os.path.join(artifact_dir, "zero_os_everything_timer.png")
        page.screenshot(path=timer_shot)
        print("Captured timer screenshot:", timer_shot, flush=True)

        # 2. Test Alarm: alarm 7am
        page.fill("#androidSearchInput", "alarm 7am")
        time.sleep(0.5)
        alarm_shot = os.path.join(artifact_dir, "zero_os_everything_alarm.png")
        page.screenshot(path=alarm_shot)
        print("Captured alarm screenshot:", alarm_shot, flush=True)

        browser.close()

if __name__ == "__main__":
    run()
