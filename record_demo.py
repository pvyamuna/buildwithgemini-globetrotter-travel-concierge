"""Script to record a demo video of Globetrotter Travel Concierge using Playwright."""

import os
import time
from playwright.sync_api import sync_playwright

RECORDING_DIR = "/config/Desktop/Session1/globetrotter-travel-concierge/demo_output"
os.makedirs(RECORDING_DIR, exist_ok=True)

APP_URL = "https://globetrotter-frontend-952170692401.us-central1.run.app"


def main():
    print("Starting Playwright demo recording...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=RECORDING_DIR,
            record_video_size={"width": 1280, "height": 800}
        )
        page = context.new_page()

        print(f"Navigating to {APP_URL}...")
        page.goto(APP_URL, wait_until="networkidle")
        time.sleep(2)

        # 1. First interaction: Click prompt chip 1 to search packages
        print("Executing Turn 1: Search packages prompt chip...")
        chip1 = page.locator(".prompt-chip").first
        if chip1.is_visible():
            chip1.click()
        else:
            page.fill("#input", "Search travel packages for Tokyo & Bali")
            page.click("button.send-btn")

        # Wait for agent response
        print("Waiting for Turn 1 response...")
        page.wait_for_selector(".msg.agent", timeout=40000)
        time.sleep(5)

        # 2. Open Preferences Modal
        print("Opening Preferences dialogue modal...")
        page.click("#open-prefs-btn")
        time.sleep(3)
        page.click("#close-prefs-btn")
        time.sleep(1)

        # 3. Second interaction: Richer prompt with tool calls & video generation
        print("Executing Turn 2: Rich prompt with video generation and budget tool...")
        page.fill("#input", "Generate a video preview of a tropical beach resort in Bali and calculate a 7-day budget.")
        page.click("button.send-btn")

        print("Waiting for Turn 2 response...")
        time.sleep(15)  # Allow time for agent response & rendering

        print("Closing page context to finish video recording...")
        page.close()
        context.close()
        browser.close()

    print(f"Demo video saved in {RECORDING_DIR}")


if __name__ == "__main__":
    main()
