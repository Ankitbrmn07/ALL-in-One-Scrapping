from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class Gadgets360Scraper(BaseScraper):
    CATEGORY = "Technology"
    BASE_URL = "https://www.gadgets360.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Latest News / Featured
        try:
            # Gadgets360 usually has a clear 'story_list' or featured section
            articles = await self.page.locator(".story_list li, .featured_story").all()
            
            for article in articles[:10]:
                try:
                    title_el = article.locator(".nlist_title a, .featured_title a").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        
                        summary_el = article.locator(".nlist_desc, .featured_intro").first
                        summary = await summary_el.inner_text() if await summary_el.count() > 0 else ""

                        items.append({
                            "title": title.strip(),
                            "short_description": summary.strip(),
                            "sub_category": "Tech News",
                            "source_url": link if link.startswith("http") else f"{self.BASE_URL}{link.lstrip('/')}",
                            "author": "Gadgets 360"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Gadgets 360: {e}")

        return items
