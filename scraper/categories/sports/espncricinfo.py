from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ESPNCricinfoScraper(BaseScraper):
    CATEGORY = "Sports"
    BASE_URL = "https://www.espncricinfo.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Matches / News
        try:
            # Look for news articles which are often in a story-grid or similar
            articles = await self.page.locator(".ds-grow > div > a").all() # Generic wrapper selector for stories
            
            # Refined selector for story cards if generic fails
            if not articles:
                articles = await self.page.locator("a.ds-block").all()

            for article in articles[:12]:
                try:
                    # Filter for actual content links, not just nav links
                    link = await article.get_attribute("href")
                    if link and ("/story/" in link or "/series/" in link):
                         title_el = article.locator("h2, span.ds-text-title-s").first
                         if await title_el.count() > 0:
                             title = await title_el.inner_text()
                             
                             summary_el = article.locator("p").first
                             summary = await summary_el.inner_text() if await summary_el.count() > 0 else "Cricket Update"

                             items.append({
                                "title": title.strip(),
                                "short_description": summary.strip(),
                                "sub_category": "Cricket",
                                "source_url": link if link.startswith("http") else f"https://www.espncricinfo.com{link}",
                                "author": "ESPN Cricinfo"
                             })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping ESPN Cricinfo: {e}")

        return items
