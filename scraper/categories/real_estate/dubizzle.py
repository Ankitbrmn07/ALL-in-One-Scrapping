
import asyncio
import logging
from typing import List, Dict
from scraper.core.base_scraper import BaseScraper
from scraper.utils.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class DubizzleScraper(BaseScraper):
    CATEGORY = "Real Estate"
    BASE_URL = "https://dubai.dubizzle.com/en/property-for-sale/residential/"

    async def extract_items(self) -> List[Dict]:
        """
        Extract items from the current page.
        This is used by the base `scrape` method, but we will override `scrape` 
        to handle the specific multi-page and detail-page flow required.
        """
        return []

    async def scrape(self) -> List[Dict]:
        """
        Orchestrates the scraping process:
        1. Navigate to listing page.
        2. Collect listing URLs across multiple pages.
        3. Visit each listing URL to extract detailed data.
        """
        self.data = []
        try:
            # 1. Navigate to Homepage / Listing Page
            await self.navigate(self.BASE_URL)
            
            # 2. Collect Listing URLs (Pagination Handling)
            listing_urls = await self._collect_listing_urls(max_pages=3) # Limit pages for safety
            logger.info(f"[{self.CATEGORY}] Found {len(listing_urls)} unique listings to scrape.")
            
            # 3. Visit each listing
            for i, url in enumerate(listing_urls):
                try:
                    logger.info(f"[{self.CATEGORY}] Scraping details for ({i+1}/{len(listing_urls)}): {url}")
                    details = await self._scrape_detail_page(url)
                    if details:
                        self.data.append(details)
                    
                    # Random delay between requests
                    import random
                    await asyncio.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    logger.error(f"Failed to scrape listing {url}: {e}")
                    continue

            return self.data

        except Exception as e:
            logger.error(f"Error during Dubizzle scraping: {e}")
            return []

    async def _collect_listing_urls(self, max_pages: int) -> List[str]:
        """
        Iterates through pages and collects all listing URLs.
        """
        collected_urls = set()
        current_page = 1
        
        while current_page <= max_pages:
            logger.info(f"[{self.CATEGORY}] Scanning page {current_page}...")
            
            # Wait for listings to load
            try:
                await self.page.wait_for_selector("[data-testid='listing-card'], article", timeout=15000)
            except:
                logger.warning(f"Timeout waiting for listings on page {current_page}")
                break

            # Extract URLs from current page
            # Selectors based on inspection and common patterns
            links = await self.page.evaluate("""
                () => {
                    const anchors = Array.from(document.querySelectorAll("[data-testid='listing-card'] a, article a"));
                    return anchors.map(a => a.href).filter(href => href.includes('/property-for-sale/') || href.includes('/property-for-rent/'));
                }
            """)
            
            new_urls = set(links) - collected_urls
            logger.info(f"Found {len(new_urls)} new listings on page {current_page}.")
            collected_urls.update(links)
            
            # Pagination Logic
            # Check for "Next" button
            next_button = self.page.locator("button[data-testid='page-next'], a[aria-label='Next Page'], button:has-text('Next')").first
            
            if await next_button.count() > 0 and await next_button.is_visible():
                try:
                    await next_button.click()
                    await self.page.wait_for_load_state('networkidle')
                    await asyncio.sleep(3)
                    current_page += 1
                except Exception as e:
                    logger.warning(f"Failed to click next page: {e}")
                    break
            else:
                logger.info("No next page found. Stopping pagination.")
                break
                
        return list(collected_urls)

    async def _scrape_detail_page(self, url: str) -> Dict:
        """
        Navigates to a specific listing URL and extracts detailed data.
        """
        await self.navigate(url)
        
        # Extract Data
        data = {
            "source_url": url,
            "scraped_at": TextCleaner.clean(str(asyncio.get_event_loop().time())), # Timestamp
            "title": await self._get_text("h1"),
            "price": await self._get_price(),
            "address": await self._get_address(),
            "description": await self._get_text("[data-testid='description-content'], .description-text"),
            "amenities": await self._get_amenities(),
            "images": await self._get_images(),
            "property_type": "Residential", # Default for this scraper
            "id": url.split('/')[-2] if url.endswith('/') else url.split('/')[-1] # Simple ID extraction from URL
        }
        
        # Clean Data
        for key, val in data.items():
            if isinstance(val, str):
                data[key] = TextCleaner.clean(val)
                
        return data

    async def _get_text(self, selector: str) -> str:
        try:
            if await self.page.locator(selector).count() > 0:
                return await self.page.locator(selector).first.inner_text()
        except:
            pass
        return "N/A"

    async def _get_price(self) -> str:
        # Dubizzle price is usually prominent
        selectors = ["[data-testid='listing-price']", ".listing-price", "h2:has-text('AED')"]
        for sel in selectors:
            try:
                if await self.page.locator(sel).count() > 0:
                    text = await self.page.locator(sel).first.inner_text()
                    # Extract numeric part if needed, but returning raw string for now
                    return text
            except: continue
        return "0"

    async def _get_address(self) -> str:
        # Address is often under title
        selectors = ["[data-testid='listing-location']", "span[data-testid='location-address']"]
        for sel in selectors:
            try:
                if await self.page.locator(sel).count() > 0:
                    return await self.page.locator(sel).first.inner_text()
            except: continue
        return "N/A"

    async def _get_amenities(self) -> str:
        # Beds, Baths, Size
        amenities = []
        try:
            # Look for specific amenity icons/labels
            # e.g. "2 Beds", "3 Baths", "1200 sqft"
            items = await self.page.locator("[data-testid='listing-key-fact']").all_inner_texts()
            if items:
                amenities = items
            else:
                # Fallback to general text search in certain areas
                pass
        except:
            pass
        return ", ".join(amenities) if amenities else "N/A"

    async def _get_images(self) -> str:
        # Extract all image URLs
        images = []
        try:
            # Look for gallery images
            imgs = await self.page.locator("[data-testid='gallery-image'] img, .image-gallery-slide img").all()
            for img in imgs:
                src = await img.get_attribute("src")
                if src:
                    images.append(src)
        except:
            pass
        return ", ".join(images)
