import asyncio
import logging
import sys
import os

# Add the current directory to path so we can import scraper
sys.path.append(os.getcwd())

from scraper.core.browser_manager import BrowserManager
from scraper.categories.business.business_insider import BusinessInsiderScraper

async def test_bi_scraper():
    logging.basicConfig(level=logging.INFO)
    
    async with BrowserManager(headless=True) as bm:
        page = await bm.get_page()
        scraper = BusinessInsiderScraper(page)
        
        print("Starting test scrape for Business Insider...")
        
        # We'll run the real scrape but we can limit it by monkeypatching the article urls list if needed
        # For now, let's just run it. 
        results = await scraper.scrape()
        print(f"\nTest complete. Scraped {len(results)} items.")
        for item in results:
            print(f"- {item['Title']} ({item['Source']})")

if __name__ == "__main__":
    asyncio.run(test_bi_scraper())
