import asyncio
import logging
import os
from scraper.core.browser_manager import BrowserManager
# Imports
from scraper.categories.biography.wikipedia import WikipediaScraper
from scraper.categories.politics.bbc import BBCScraper
from scraper.categories.health.healthline import HealthlineScraper
from scraper.categories.bollywood.filmibeat import FilmiBeatScraper
from scraper.categories.bollywood.bollywoodhungama import BollywoodHungamaScraper
from scraper.categories.bollywood.imdb import IMDbScraper
from scraper.categories.health.who import WHOScraper
from scraper.categories.health.nih import NIHScraper
from scraper.categories.fitness.healthline_fitness import HealthlineFitnessScraper
from scraper.categories.fitness.menshealth import MensHealthScraper
from scraper.categories.technology.gadgets360 import Gadgets360Scraper
from scraper.categories.sports.espncricinfo import ESPNCricinfoScraper
from scraper.categories.sports.sportskeeda import SportskeedaScraper
from scraper.categories.travel.lonelyplanet import LonelyPlanetScraper
from scraper.categories.fashion.fashionunited import FashionUnitedScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRAPERS = [
    ("Biography", "Wikipedia", WikipediaScraper),
    ("Politics", "BBC", BBCScraper),
    ("Health", "Healthline", HealthlineScraper),
    ("Health", "WHO", WHOScraper),
    ("Health", "NIH", NIHScraper),
    ("Bollywood", "FilmiBeat", FilmiBeatScraper),
    ("Bollywood", "Bollywood Hungama", BollywoodHungamaScraper),
    ("Bollywood", "IMDb", IMDbScraper),
    ("Fitness", "Healthline Fitness", HealthlineFitnessScraper),
    ("Fitness", "Men's Health", MensHealthScraper),
    ("Technology", "Gadgets 360", Gadgets360Scraper),
    ("Sports", "ESPN Cricinfo", ESPNCricinfoScraper),
    ("Sports", "Sportskeeda", SportskeedaScraper),
    ("Travel", "Lonely Planet", LonelyPlanetScraper),
    ("Fashion", "Fashion United", FashionUnitedScraper),
]

async def test_scraper(name, scraper_cls, page):
    logger.info(f"--------------------------------------------------")
    logger.info(f"Testing: {name}")
    try:
        scraper = scraper_cls(page)
        data = await scraper.scrape()
        count = len(data)
        if count > 0:
            logger.info(f"✅ SUCCESS: {name} - Scraped {count} items")
            # Log first item title for verification
            first_title = data[0].get('title', 'No Title')
            logger.info(f"   Sample: {first_title}")
            return True, name, count
        else:
            logger.warning(f"⚠️ WARNING: {name} - Scraped 0 items (Structure might have changed)")
            return False, name, 0
    except Exception as e:
        logger.error(f"❌ FAILED: {name} - Error: {str(e)}")
        return False, name, str(e)

async def run_all_tests():
    results = []
    
    logger.info("Starting Browser...")
    async with BrowserManager(headless=True) as bm:
        page = await bm.get_page()
        
        for category, name, scraper_cls in SCRAPERS:
            success, scraper_name, result = await test_scraper(f"{category} - {name}", scraper_cls, page)
            results.append((success, scraper_name, result))
            
    logger.info("==================================================")
    logger.info("FINAL REPORT")
    logger.info("==================================================")
    for success, name, result in results:
        status = "✅ PASS" if success else "❌ FAIL" if isinstance(result, str) else "⚠️ EMPTY"
        detail = f"{result} items" if isinstance(result, int) else result
        logger.info(f"{status} | {name:<35} | {detail}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
