from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class WHOScraper(BaseScraper):
    CATEGORY = "Health"
    BASE_URL = "https://www.who.int/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Main Carousel / Feature
        try:
            # Attempt to find the main carousel or featured item
            featured_items = await self.page.locator(".sf-carousel-item, .homepage-feature").all()
            for item in featured_items[:5]:
                try:
                    title_el = item.locator("h2 a, .heading a").first
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        
                        items.append({
                            "title": title.strip(),
                            "short_description": "Featured Health Topic",
                            "sub_category": "Featured",
                            "source_url": link if link.startswith("http") else f"https://www.who.int{link}",
                            "author": "WHO"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping WHO featured: {e}")

        # 2. Latest News
        try:
            news_items = await self.page.locator(".list-view--item, .vertical-list-item").all()
            for item in news_items[:10]:
                try:
                    title_el = item.locator(".heading").first
                    date_el = item.locator(".timestamp").first
                    
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link_el = item.locator("a").first
                        link = await link_el.get_attribute("href")
                        
                        date = await date_el.inner_text() if await date_el.count() > 0 else ""

                        items.append({
                            "title": title.strip(),
                            "short_description": f"Date: {date}",
                            "sub_category": "Latest News",
                            "source_url": link if link.startswith("http") else f"https://www.who.int{link}",
                            "author": "WHO"
                        })
                except:
                    continue
        except:
            pass

        return items
