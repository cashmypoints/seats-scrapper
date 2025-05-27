
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def scrape_seats_aero(origin="DEL", destination="YVR", date="2025-10-16"):
    url = f"https://seats.aero/search?min_seats=1&applicable_cabin=any&additional_days_num=1&max_fees=40000&date={date}&origins={origin}&destinations={destination}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        print(f"🔍 Searching {origin} → {destination} on {date}...")

        # wait for any text content or fallback element to ensure the page loaded
await page.wait_for_selector("body", timeout=20000)

# Optional: take a screenshot to verify
await page.screenshot(path="debug.png", full_page=True)

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
        print(df)
        df.to_csv("results.csv", index=False)

asyncio.run(scrape_seats_aero())
