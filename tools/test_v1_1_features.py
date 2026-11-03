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

        # 1. Start a real timer: 10 mins
        page.fill("#androidSearchInput", "timer 10 mins")
        time.sleep(0.5)
        # Click Start Timer
        page.click(".tray-btn.primary")
        time.sleep(1.5) # Wait for countdown to tick
        timer_shot = os.path.join(artifact_dir, "zero_os_active_timer_running.png")
        page.screenshot(path=timer_shot)
        print("Captured running timer screenshot:", timer_shot, flush=True)

        # 2. Set an alarm: 7am
        page.fill("#androidSearchInput", "alarm 7am")
        time.sleep(0.5)
        page.click(".tray-btn.primary")
        time.sleep(1.0)
        alarm_shot = os.path.join(artifact_dir, "zero_os_active_alarm_set.png")
        page.screenshot(path=alarm_shot)
        print("Captured active alarm screenshot:", alarm_shot, flush=True)

        # 3. Test false trigger prevention: "India weather"
        page.fill("#androidSearchInput", "India weather")
        time.sleep(0.5)
        india_shot = os.path.join(artifact_dir, "zero_os_india_weather_safe.png")
        page.screenshot(path=india_shot)
        print("Captured India weather safe check screenshot:", india_shot, flush=True)

        browser.close()

if __name__ == "__main__":
    run()
