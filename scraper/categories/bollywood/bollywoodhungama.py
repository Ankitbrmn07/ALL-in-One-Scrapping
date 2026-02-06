from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class BollywoodHungamaScraper(BaseScraper):
    CATEGORY = "Bollywood"
    BASE_URL = "https://www.bollywoodhungama.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Main Featured News (Center Stage)
        # Selectors are approximated based on general news site structures
        # as live inspection isn't available.
        try:
            featured = await self.page.locator("article.featured").all()
            if not featured:
                 featured = await self.page.locator(".bh-slider-item").all() # Fallback for sliders

            for article in featured[:5]:
                try:
                    title_el = article.locator("h2 a, h3 a").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        desc_el = article.locator("p").first
                        desc = await desc_el.inner_text() if await desc_el.count() > 0 else ""

                        items.append({
                            "title": title.strip(),
                            "short_description": desc.strip(),
                            "sub_category": "Featured",
                            "source_url": link,
                            "author": "Bollywood Hungama"
                        })
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping featured items: {e}")

        # 2. Latest News
        try:
            news_list = await self.page.locator(".latest-news li, article.news-item").all()
            for item in news_list[:10]:
                try:
                    title_el = item.locator("a.title, h3 a").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        
                        items.append({
                            "title": title.strip(),
                            "short_description": "Latest Bollywood News",
                            "sub_category": "Latest News",
                            "source_url": link,
                            "author": "Bollywood Hungama"
                        })
                except Exception:
                    continue
        except Exception:
            pass

        return items
