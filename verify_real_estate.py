
import asyncio
import logging
from scraper.core.browser_manager import BrowserManager
from scraper.categories.real_estate import DubizzleScraper, BayutScraper, PropertyFinderScraper, EmaarScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scraper(name, scraper_cls):
    print(f"\n--- Testing {name} ---")
    try:
        async with BrowserManager(headless=True) as bm:
            page = await bm.get_page()
            scraper = scraper_cls(page)
            # We don't want to run full scrape, just check if it can navigate
            # But scraper.scrape() is the main entry.
            # We can mock navigate/extract or just let it run for a few seconds.
            # For this test, let's just try to instantiate and maybe navigate.
            await scraper.navigate(scraper.BASE_URL)
            print(f"Navigation to {scraper.BASE_URL} successful.")
            
            # Optional: detailed test
            # data = await scraper.scrape()
            # print(f"Scraped {len(data)} items")
            
    except Exception as e:
        print(f"FAILED {name}: {e}")

async def main():
    await test_scraper("Dubizzle", DubizzleScraper)
    await test_scraper("Bayut", BayutScraper)
    await test_scraper("Property Finder", PropertyFinderScraper)
    await test_scraper("Emaar", EmaarScraper)

if __name__ == "__main__":
    asyncio.run(main())
