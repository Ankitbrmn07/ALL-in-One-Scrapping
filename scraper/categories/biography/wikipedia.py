from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class WikipediaScraper(BaseScraper):
    CATEGORY = "Biography"
    BASE_URL = "https://en.wikipedia.org/wiki/Main_Page"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # Selectors for Main Page features
        # 1. Today's Featured Article
        tfa_selector = "#mp-tfa"
        if await self.page.locator(tfa_selector).count() > 0:
            heading = await self.page.locator(f"{tfa_selector} p b a").first.inner_text()
            summary = await self.page.locator(f"{tfa_selector} p").first.inner_text()
            link = await self.page.locator(f"{tfa_selector} p b a").first.get_attribute("href")
            
            items.append({
                "title": heading,
                "short_description": summary,
                "sub_category": "Featured Article",
                "source_url": f"https://en.wikipedia.org{link}" if link else self.BASE_URL,
                "author": "Wikipedia Contributors"
            })

        # 2. In the news (mp-itn)
        itn_items = await self.page.locator("#mp-itn ul li").all()
        for li in itn_items:
            try:
                text = await li.inner_text()
                # Try to get the first bold link which is usually the subject
                subject_link = li.locator("b a").first
                if await subject_link.count() > 0:
                    title = await subject_link.inner_text()
                    link = await subject_link.get_attribute("href")
                    
                    items.append({
                        "title": title,
                        "short_description": text,
                        "sub_category": "In the News",
                        "source_url": f"https://en.wikipedia.org{link}" if link else self.BASE_URL,
                        "author": "Wikipedia Contributors"
                    })
            except Exception as e:
                pass

        # 3. On this day (mp-otd) - Good source for biographies (births/deaths)
        otd_items = await self.page.locator("#mp-otd ul li").all()
        for li in otd_items:
            try:
                text = await li.inner_text()
                # Rough check if it looks like a person's entry (often has birth/death years or simple names)
                # This is heuristic.
                bold_link = li.locator("b a").first
                if await bold_link.count() > 0:
                    title = await bold_link.inner_text()
                    link = await bold_link.get_attribute("href")
                    items.append({
                        "title": title,
                        "short_description": text,
                        "sub_category": "On This Day",
                        "source_url": f"https://en.wikipedia.org{link}" if link else self.BASE_URL,
                        "author": "Wikipedia Contributors"
                    })
            except:
                pass

        return items
