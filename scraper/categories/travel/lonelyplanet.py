from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class LonelyPlanetScraper(BaseScraper):
    CATEGORY = "Travel"
    BASE_URL = "https://www.lonelyplanet.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Featured / Articles
        try:
            # Lonely Planet uses various cards for articles
            articles = await self.page.locator("article a, .card a").all()
            
            for article in articles[:10]:
                try:
                    title_el = article.locator("h2, h3").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await article.get_attribute("href")
                        
                        # Sometimes title is not inside h2/h3 but is the link itself or adjacent
                        if not title:
                            title = await article.get_attribute("aria-label") or "Travel Article"

                        items.append({
                            "title": title.strip(),
                            "short_description": "Travel Guide/Article",
                            "sub_category": "Destinations",
                            "source_url": link if link.startswith("http") else f"https://www.lonelyplanet.com{link}",
                            "author": "Lonely Planet"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Lonely Planet: {e}")

        return items
