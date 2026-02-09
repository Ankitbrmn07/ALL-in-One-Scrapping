
import asyncio
import logging
from scraper.core.browser_manager import BrowserManager
from scraper.categories.real_estate.dubizzle import DubizzleScraper

logging.basicConfig(level=logging.INFO)

async def main():
    async with BrowserManager(headless=False) as bm:
        page = await bm.get_page()
        scraper = DubizzleScraper(page)
        data = await scraper.scrape()
        print(f"Scraped {len(data)} items")
        if data:
            print(data[0])

if __name__ == "__main__":
    asyncio.run(main())
