from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SportskeedaScraper(BaseScraper):
    CATEGORY = "Sports"
    BASE_URL = "https://www.sportskeeda.com/"

    async def extract_items(self) -> List[Dict]:
        items = []

        try:
            # Scrape featured/latest articles
            # Based on inspection: a.news-item contains the info
            articles = await self.page.locator("a.news-item").all()
            
            for article in articles[:15]:
                try:
                    title_el = article.locator(".news-item-content-bottom-title").first
                    if await title_el.count() > 0:
                        name = await title_el.inner_text()
                        link = await article.get_attribute("href")
                        
                        if link and not link.startswith("http"):
                             link = f"https://www.sportskeeda.com{link}"

                        # Image
                        img_el = article.locator("img.feed-element-img").first
                        img_src = ""
                        if await img_el.count() > 0:
                            img_src = await img_el.get_attribute("data-lazy") or await img_el.get_attribute("src")

                        # Date/Subtitle
                        date_el = article.locator(".news-item-content-bottom-subtitle-date").first
                        date_text = await date_el.inner_text() if await date_el.count() > 0 else ""

                        items.append({
                            "title": name.strip(),
                            "short_description": f"Sports News - {date_text}",
                            "sub_category": "Sports",
                            "source_url": link,
                            "author": "Sportskeeda",
                            "image_url": img_src
                        })
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Sportskeeda: {e}")

        return items
