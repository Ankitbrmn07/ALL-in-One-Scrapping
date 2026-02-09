
import asyncio
import logging
from typing import List, Dict
from scraper.core.base_scraper import BaseScraper
from scraper.utils.text_cleaner import TextCleaner
from datetime import datetime

logger = logging.getLogger(__name__)

class PropertyFinderScraper(BaseScraper):
    CATEGORY = "Real Estate"
    BASE_URL = "https://www.propertyfinder.ae/en/search?c=2&fu=0&rp=y&ob=mr"

    async def scrape(self) -> List[Dict]:
        self.data = []
        try:
            await self.navigate(self.BASE_URL)
            
            # Property Finder also uses Anti-bot (Cloudflare/human check).
            # Similar strategy: Collect entries on search page.
            
            urls = await self._collect_urls(max_pages=2)
            logger.info(f"[{self.CATEGORY}] Found {len(urls)} listings.")
            
            for url in urls:
                try:
                    item = await self._scrape_details(url)
                    if item:
                        self.data.append(item)
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error details {url}: {e}")
            
            return self.data
        except Exception as e:
            logger.error(f"Property Finder scrape failed: {e}")
            return []

    async def _collect_urls(self, max_pages=2):
        collected = set()
        for i in range(max_pages):
            try:
                # Wait for specific card class
                await self.page.wait_for_selector("[data-testid='property-card-addr'], .card-list__item", timeout=15000)
            except:
                break
                
            # Extract
            links = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll("a[href*='/en/plp/buy/'], a[href*='/en/plp/rent/']")).map(a => a.href);
                }
            """)
            # Fix: Property Finder search results connect to property details. 
            # The links usually look like /en/plp/buy/... or /en/rent/... NO, those might be searches.
            # Actual detail links usually contain /property/
            
            links = await self.page.evaluate("""
                () => {
                   return Array.from(document.querySelectorAll("a[href*='/property/']")).map(a => a.href);
                }
            """)
            
            collected.update(links)
            
            # Next Page
            try:
                next_btn = self.page.locator("a[aria-label='Next'], a[data-testid='pagination-next']").first
                if await next_btn.count() > 0 and await next_btn.is_visible():
                    await next_btn.click()
                    await asyncio.sleep(3)
                else: 
                    break
            except: break
            
        return list(collected)

    async def _scrape_details(self, url):
        await self.navigate(url)
        
        # Selectors (Best guess based on standard class names or aria)
        title = await self._get_text("h1")
        price = await self._get_text(".price, [data-testid='price']")
        address = await self._get_text(".location, [data-testid='property-location']")
        size = await self._get_text("[data-testid='property-size']")
        
        amenities = []
        # Look for amenity list
        items = await self.page.locator(".amenities-list__item, [data-testid='amenity-item']").all_inner_texts()
        if items: amenities = items
        
        images = []
        imgs = await self.page.locator(".image-gallery-slide img, [data-testid='gallery-image']").all()
        for img in imgs:
            src = await img.get_attribute("src")
            if src: images.append(src)

        return {
            "source_url": url,
            "title": title,
            "price": price,
            "address": address,
            "amenities": ", ".join(amenities),
            "images": ", ".join(images),
            "scraped_at": datetime.now().isoformat() 
        }

    async def _get_text(self, selector):
        try:
             if await self.page.locator(selector).count() > 0:
                 return await self.page.locator(selector).first.inner_text()
        except: pass
        return "N/A"
