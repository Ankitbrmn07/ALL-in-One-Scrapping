import asyncio
import logging
import argparse
import sys
from termcolor import colored

# Ensure the current directory is in PYTHONPATH
sys.path.append(".")

from scraper.core.browser_manager import BrowserManager
from scraper.core.exporter import Exporter

# Import Scrapers
from scraper.categories.biography.wikipedia import WikipediaScraper
from scraper.categories.politics.bbc import BBCScraper
from scraper.categories.health.healthline import HealthlineScraper

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ScraperRunner")

async def run_scraper(category: str, site: str, headless: bool):
    logger.info(colored(f"Initializing Scraper for Category: {category}, Site: {site}", "cyan"))
    
    async with BrowserManager(headless=headless) as bm:
        page = await bm.get_page()
        
        scraper = None
        if site.lower() == "wikipedia":
            scraper = WikipediaScraper(page)
        elif site.lower() == "bbc":
            scraper = BBCScraper(page)
        elif site.lower() == "healthline":
            scraper = HealthlineScraper(page)
        
        if not scraper:
            logger.error(colored(f"No scraper found for site: {site}", "red"))
            return

        logger.info("Starting extraction...")
        data = await scraper.scrape()
        
        if data:
            logger.info(colored(f"Extracted {len(data)} records.", "green"))
            
            # Export
            filename = f"data/{category}/{site}_data.csv"
            Exporter.to_csv(data, filename)
            
            # Also generic dump
            Exporter.to_json(data, f"data/{category}/{site}_data.json")
        else:
            logger.warning("No data extracted.")

def main():
    parser = argparse.ArgumentParser(description="Category-Based Web Scraper Runner")
    parser.add_argument("--category", type=str, default="biography", help="Category to scrape (e.g., biography, politics)")
    parser.add_argument("--site", type=str, required=True, help="Site to scrape (e.g., wikipedia, bbc)")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (visible)")
    
    args = parser.parse_args()
    
    asyncio.run(run_scraper(args.category, args.site, not args.headed))

if __name__ == "__main__":
    main()
