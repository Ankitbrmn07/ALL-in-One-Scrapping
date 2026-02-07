import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from playwright.async_api import Page
from scraper.utils.text_cleaner import TextCleaner
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract Base Class for all category scrapers.
    """
    CATEGORY = "General"
    BASE_URL = ""

    def __init__(self, page: Page):
        self.page = page
        self.data = []

    async def navigate(self, url: str = None):
        target_url = url or self.BASE_URL
        if not target_url:
            raise ValueError("No URL provided for navigation")
        
        logger.info(f"[{self.CATEGORY}] Navigating to {target_url}...")
        try:
            await self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2) # Human-like pause
        except Exception as e:
            logger.error(f"Navigation failed: {e}")

    async def extract_items(self) -> List[Dict]:
        """
        Main logic to identify and extract items from the listing page.
        Should return a list of dictionaries.
        """
        return []

    async def scrape(self) -> List[Dict]:
        """
        Orchestrates the scraping process: Navigate -> Extract -> Return.
        """
        try:
            await self.navigate()
            items = await self.extract_items()
            
            # Post-processing / Standardization
            standardized_items = []
            for item in items:
                item['category'] = self.CATEGORY
                item['website'] = self.BASE_URL
                item['scraped_at'] = datetime.now().isoformat()
                
                # Clean text fields
                for key, val in item.items():
                    if isinstance(val, str):
                        item[key] = TextCleaner.clean(val)
                
                standardized_items.append(item)
            
            self.data = standardized_items
            logger.info(f"[{self.CATEGORY}] Scraped {len(self.data)} items.")
            return self.data
            
        except Exception as e:
            logger.error(f"Error during scraping {self.CATEGORY}: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def handle_captcha(self):
        """
        Placeholder for manual or automated CAPTCHA handling.
        """
        # Simple check for common captcha keywords in title or body
        title = await self.page.title()
        if "captcha" in title.lower() or "challenge" in title.lower():
            logger.warning("CAPTCHA detected! Pausing for manual intervention...")
            # In a real scenario, we might wait for user input or element disappearance
            # For now, we wait a bit
            await asyncio.sleep(10)
