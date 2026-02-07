import asyncio
import logging
import sys
import os

sys.path.append(os.getcwd())

from scraper.core.browser_manager import BrowserManager
from scraper.categories.business.business_insider import BusinessInsiderScraper

async def minimal_test():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger(__name__)
    
    try:
        async with BrowserManager(headless=True) as bm:
            page = await bm.get_page()
            scraper = BusinessInsiderScraper(page)
            print("Navigating to Business Insider...")
            await scraper.page.goto(scraper.BASE_URL, wait_until="domcontentloaded", timeout=60000)
            print(f"Page title: {await scraper.page.title()}")
            
            # Test one locator count
            count = await scraper.page.locator("h2, h3").count()
            print(f"Found {count} headings.")
            
    except Exception as e:
        print(f"Minimal test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(minimal_test())
