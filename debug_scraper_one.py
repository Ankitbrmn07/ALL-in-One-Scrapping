import asyncio
import logging
import sys
from playwright.async_api import async_playwright
from scraper.categories.bollywood.bollywoodhungama import BollywoodHungamaScraper
from scraper.categories.bollywood.imdb import IMDbScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_scraper(scraper_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Headless=False to see what's happening
        page = await browser.new_page()

        if scraper_name == "bollywoodhungama":
            scraper = BollywoodHungamaScraper(page)
        elif scraper_name == "imdb":
            scraper = IMDbScraper(page)
        else:
            print(f"Unknown scraper: {scraper_name}")
            return

        print(f"Starting scraper: {scraper_name}")
        try:
            data = await scraper.scrape()
            print(f"Scraped {len(data)} items:")
            for item in data[:5]:  # Print first 5 items
                print(item)
        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_scraper_one.py <scraper_name>")
        print("Available scrapers: bollywoodhungama, imdb")
    else:
        asyncio.run(debug_scraper(sys.argv[1]))
