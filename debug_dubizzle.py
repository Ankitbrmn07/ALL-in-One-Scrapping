
import asyncio
from scraper.core.browser_manager import BrowserManager

async def main():
    async with BrowserManager(headless=False) as bm:
        page = await bm.get_page()
        print("Navigating...")
        await page.goto("https://dubai.dubizzle.com/en/property-for-sale/residential/", wait_until="domcontentloaded")
        await page.wait_for_timeout(20000) # Wait for Incapsula
        content = await page.content()
        with open("dubizzle_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Done dumping HTML.")

if __name__ == "__main__":
    asyncio.run(main())
