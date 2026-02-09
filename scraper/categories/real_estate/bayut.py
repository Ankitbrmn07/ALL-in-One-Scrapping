
import asyncio
import logging
from typing import List, Dict
from scraper.core.base_scraper import BaseScraper
from scraper.utils.text_cleaner import TextCleaner
from datetime import datetime

logger = logging.getLogger(__name__)

class BayutScraper(BaseScraper):
    CATEGORY = "Real Estate"
    BASE_URL = "https://www.bayut.com/for-sale/property/uae/"

    async def scrape(self) -> List[Dict]:
        self.data = []
        try:
            await self.navigate(self.BASE_URL)
            
            # Bayut also has Cloudflare/Anti-bot. 
            # We'll try to iterate listings on the main page.
            
            # Collect listing URLs
            listing_urls = await self._collect_listing_urls(max_pages=3)
            logger.info(f"[{self.CATEGORY}] Found {len(listing_urls)} listings.")
            
            for url in listing_urls:
                try:
                    # In a real scenario, we might want to just extract from the listing card to be faster/safer
                    # But requirement says "From the listing detail page".
                    item = await self._scrape_detail(url)
                    if item:
                        self.data.append(item)
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    
            return self.data
            
        except Exception as e:
            logger.error(f"Bayut scrape failed: {e}")
            return []

    async def _collect_listing_urls(self, max_pages=3) -> List[str]:
        urls = set()
        for i in range(max_pages):
            # Wait for listings
            try:
                await self.page.wait_for_selector("article, [role='article']", timeout=15000)
            except:
                break
                
            # Extract links
            # Bayut listing cards often have a link to the details
            links = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll("article a")).map(a => a.href)
                        .filter(h => h.includes('/property/details'));
                }
            """)
            urls.update(links)
            
            # Next page
            # Bayut simplified pagination
            next_btn = self.page.locator("a[title='Next'], button[title='Next']").first
            if await next_btn.count() > 0 and await next_btn.is_visible():
                await next_btn.click()
                await asyncio.sleep(3)
            else:
                break
                
        return list(urls)

    async def _scrape_detail(self, url):
        await self.navigate(url)
        
        # Bayut Detail Selectors (approximate based on common React class names or aria-labels)
        title = await self._get_text("h1")
        price = await self._get_text("[aria-label='Price']")
        address = await self._get_text("[aria-label='Location']")
        description = await self._get_text("[aria-label='Property Description']")
        
        # Amenities
        amenities = []
        # Bayut has an amenities section
        amenities_texts = await self.page.locator("._190bb598").all_inner_texts() # Random class example
        if not amenities_texts:
             amenities_texts = await self.page.locator("h2:has-text('Amenities') + div").all_inner_texts()
        
        images = []
        imgs = await self.page.locator("[aria-label='Property Image'] img").all()
        for img in imgs:
            src = await img.get_attribute("src")
            if src: images.append(src)
            
        return {
            "source_url": url,
            "title": title,
            "price": price,
            "address": address,
            "description": description,
            "amenities": ", ".join(amenities_texts) if amenities_texts else "N/A",
            "images": ", ".join(images),
            "scraped_at": datetime.now().isoformat()
        }

    async def _get_text(self, selector):
        try:
            return await self.page.locator(selector).first.inner_text()
        except:
            return "N/A"
