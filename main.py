import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import shutil
import os

async def scrape_seats_aero(origin="DEL", destination="YVR", date="2025-10-16"):
    url = f"https://seats.aero/search?min_seats=1&applicable_cabin=any&additional_days_num=1&max_fees=40000&date={date}&origins={origin}&destinations={destination}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless=False for local testing
        page = await browser.new_page()
        print(f"🔍 Searching {origin} → {destination} on {date}...")
        await page.goto(url)

        # Wait for basic content to load
        await page.wait_for_selector("body", timeout=20000)

        # Take a screenshot for debugging
        await page.screenshot(path="debug.png", full_page=True)

        # Save full HTML dump
        html = await page.content()
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Try extracting table data
        rows = await page.query_selector_all("tbody tr")
        if not rows:
            print("❌ No flight results found.")
            await browser.close()
            return

        print(f"✅ Found {len(rows)} results!")

        results = []
        for row in rows:
            cells = await row.query_selector_all("td")
            values = [await cell.inner_text() for cell in cells]
            results.append(values)

        await browser.close()

        df = pd.DataFrame(results)
        df.columns = ["Date", "From", "To", "Program", "Cabin", "Points", "Fees", "Seats", "Airline", "Source"]
        df.to_csv("results.csv", index=False)
        print("✅ Saved results.csv")

        # ✅ Create output folder and copy all files into it
        os.makedirs("output", exist_ok=True)
        shutil.copy("results.csv", "output/results.csv")
        shutil.copy("debug.png", "output/debug.png")
        shutil.copy("page_dump.html", "output/page_dump.html")

asyncio.run(scrape_seats_aero())
