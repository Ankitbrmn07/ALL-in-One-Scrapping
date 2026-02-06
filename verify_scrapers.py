import logging
import asyncio
from unittest.mock import MagicMock

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_imports():
    try:
        logger.info("Verifying imports...")
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
        
        logger.info("All imports successful!")
        return True
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return False

def verify_instantiation():
    try:
        logger.info("Verifying class instantiation...")
        from api_server import SCRAPER_CLASSES
        
        mock_page = MagicMock()
        
        for key, cls in SCRAPER_CLASSES.items():
            logger.info(f"Instantiating {key} -> {cls.__name__}")
            try:
                scraper = cls(mock_page)
                # Verify it has extract_items method
                if not hasattr(scraper, 'extract_items'):
                    logger.error(f"{cls.__name__} missing extract_items method")
                    return False
            except Exception as e:
                logger.error(f"Instantiation failed for {key}: {e}")
                return False
                
        logger.info("All classes instantiated successfully!")
        return True
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    if verify_imports() and verify_instantiation():
        print("VERIFICATION SUCCESS: All scrapers are valid.")
    else:
        print("VERIFICATION FAILED")
