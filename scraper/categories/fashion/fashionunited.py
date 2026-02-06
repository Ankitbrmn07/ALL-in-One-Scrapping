from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class FashionUnitedScraper(BaseScraper):
    CATEGORY = "Fashion"
    BASE_URL = "https://fashionunited.in/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Latest News
        try:
            articles = await self.page.locator(".news-item, .MuiGrid-item").all()
            
            for article in articles[:10]:
                try:
                    title_el = article.locator("h2, h3, .MuiTypography-h5").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link_el = article.locator("a").first
                        link = await link_el.get_attribute("href")
                        
                        summary_el = article.locator("p").first
                        summary = await summary_el.inner_text() if await summary_el.count() > 0 else "Fashion News"

                        items.append({
                            "title": title.strip(),
                            "short_description": summary.strip(),
                            "sub_category": "Fashion News",
                            "source_url": link if link.startswith("http") else f"https://fashionunited.in{link}",
                            "author": "Fashion United"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Fashion United: {e}")

        return items
