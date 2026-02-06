from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class BollywoodHungamaScraper(BaseScraper):
    CATEGORY = "Bollywood"
    BASE_URL = "https://www.bollywoodhungama.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Main Featured News & Latest News
        # Based on inspection, items are in .bh-grid-post-container or .hentry
        try:
            # We target the specific grid containers we saw in the dump
            article_containers = await self.page.locator(".bh-grid-post-container").all()
            
            for container in article_containers[:15]:  # Get first 15 items
                try:
                    # Title and Link are usually in .bh-title h2 a
                    title_el = container.locator(".bh-title h2 a").first
                    
                    if await title_el.count() > 0:
                        name = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        
                        # Description might be missing or in a different place, but we have title
                        # Try to get image if possible
                        img_el = container.locator("figure img").first
                        img_src = ""
                        if await img_el.count() > 0:
                             img_src = await img_el.get_attribute("data-src") or await img_el.get_attribute("src")

                        desc = "Bollywood News" # Default description as text is minimal in grid

                        items.append({
                            "title": name.strip(),
                            "short_description": desc,
                            "sub_category": "Featured", # Simplifying to one category for now
                            "source_url": link,
                            "author": "Bollywood Hungama",
                            "image_url": img_src
                        })
                except Exception as e:
                    # logger.warning(f"Error scraping individual item: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Bollywood Hungama items: {e}")

        return items
