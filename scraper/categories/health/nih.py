from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class NIHScraper(BaseScraper):
    CATEGORY = "Health"
    BASE_URL = "https://www.nih.gov/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Top Stories / News
        try:
            # NIH typically has a 'Top Stories' section
            articles = await self.page.locator(".views-row article, .card").all()
            
            for article in articles[:8]:
                try:
                    title_el = article.locator("h2 a, h3 a").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        
                        teaser_el = article.locator("p, .teaser").first
                        teaser = await teaser_el.inner_text() if await teaser_el.count() > 0 else ""

                        items.append({
                            "title": title.strip(),
                            "short_description": teaser.strip(),
                            "sub_category": "Research News",
                            "source_url": link if link.startswith("http") else f"https://www.nih.gov{link}",
                            "author": "NIH"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping NIH: {e}")

        return items
