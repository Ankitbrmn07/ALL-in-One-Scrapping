from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SportskeedaScraper(BaseScraper):
    CATEGORY = "Sports"
    BASE_URL = "https://www.sportskeeda.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Trending / Featured
        try:
            articles = await self.page.locator(".feed-item, .listing-story").all()
            
            for article in articles[:10]:
                try:
                    title_el = article.locator(".title a, h2 a").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        
                        items.append({
                            "title": title.strip(),
                            "short_description": "Sports News",
                            "sub_category": "General Sports",
                            "source_url": link if link.startswith("http") else f"https://www.sportskeeda.com{link}",
                            "author": "Sportskeeda"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Sportskeeda: {e}")

        return items
