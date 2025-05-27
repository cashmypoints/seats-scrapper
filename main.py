import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def scrape_seats_aero(origin="DEL", destination="YVR", date="2025-10-16"):
    url = f"https://seats.aero/search?min_seats=1&applicable_cabin=any&additional_days_num=1&max_fees=40000&date={date}&origins={origin}&destinations={destination}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set headless=False to debug locally
        page = await browser.new_page()
        print(f"🔍 Searching {origin} → {destination} on {date}...")
        await page.goto(url)

        # Wait for some stable element like <body>
        await page.wait_for_selector("body", timeout=20000)

        # Take screenshot to debug what page looks like
        await page.screenshot(path="debug.png", full_page=True)

        # Dump HTML for investigation
        html = await page.content()
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Try to locate results table rows
        rows = await page.query_selector_all("tbody tr")
        if not rows:
            print("❌ No flight results found.")
            await browser.close()
            return

        print(f"✅ Found {len(rows)} results!")

        # Extract row data
        results = []
        for row in rows:
            cells = await row.query_selector_all("td")
            values = [await cell.inner_text() for cell in cells]
            results.append(values)

        await browser.close()

        # Convert to DataFrame and save
        df = pd.DataFrame(results)
        df.columns = ["Date", "From", "To", "Program", "Cabin", "Points", "Fees", "Seats", "Airline", "Source"]
        df.to_csv("results.csv", index=False)
        print("✅ Saved results.csv")

asyncio.run(scrape_seats_aero())
