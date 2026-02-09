
import asyncio
import logging
from typing import List, Dict
from scraper.core.base_scraper import BaseScraper
from scraper.utils.text_cleaner import TextCleaner
from datetime import datetime

logger = logging.getLogger(__name__)

class EmaarScraper(BaseScraper):
    CATEGORY = "Real Estate"
    BASE_URL = "https://properties.emaar.com/en/our-communities/"

    async def scrape(self) -> List[Dict]:
        self.data = []
        try:
            await self.navigate(self.BASE_URL)
            
            # Emaar "Our Communities" page lists projects/communities.
            # We will treat each community card as a listing, or find a search endpoint.
            # The structure usually has cards with "Starting Price", "Location", "Title".
            
            # 1. Collect Listing URLs (Project Links)
            project_links = await self._collect_project_links()
            logger.info(f"[{self.CATEGORY}] Found {len(project_links)} projects.")
            
            # 2. Visit details
            for url in project_links:
                try:
                    item = await self._scrape_project(url)
                    if item:
                        self.data.append(item)
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error scraping Emaar project {url}: {e}")
                    
            return self.data
        except Exception as e:
            logger.error(f"Emaar scrape failed: {e}")
            return []

    async def _collect_project_links(self) -> List[str]:
        # Wait for cards
        try:
            await self.page.wait_for_selector(".community-card, .project-card, a.card", timeout=15000)
        except:
             pass
             
        # Extract hrefs
        links = await self.page.evaluate("""
            () => {
                const anchors = Array.from(document.querySelectorAll(".community-card a, .project-card a, a.card"));
                return anchors.map(a => a.href).filter(h => h.includes('/en/')); 
            }
        """)
        return list(set(links))

    async def _scrape_project(self, url):
        await self.navigate(url)
        
        # Scrape Details
        title = await self._get_text("h1")
        price = await self._get_text(".price, .starting-price")
        description = await self._get_text(".description, .project-description")
        
        # Images
        images = []
        imgs = await self.page.locator(".gallery img, .slider img").all()
        for img in imgs:
            src = await img.get_attribute("src")
            if src: images.append(src)
            
        # Amenities
        amenities = await self.page.locator(".amenities-list li, .features li").all_inner_texts()
        
        return {
            "source_url": url,
            "title": title,
            "price": price,
            "description": description,
            "amenities": ", ".join(amenities) if amenities else "N/A",
            "images": ", ".join(images),
            "address": "Dubai, UAE", # Default for Emaar
            "scraped_at": datetime.now().isoformat()
        }

    async def _get_text(self, selector):
        try:
            return await self.page.locator(selector).first.inner_text()
        except:
            return "N/A"
