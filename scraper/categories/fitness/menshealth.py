from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class MensHealthScraper(BaseScraper):
    CATEGORY = "Fitness"
    BASE_URL = "https://www.menshealth.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # 1. Top Stories / Hero
        try:
            # Men's Health often uses standard Hearst magazine layout
            articles = await self.page.locator(".item-title, .custom-item-title").all()
            
            for article in articles[:10]:
                try:
                    title = await article.inner_text()
                    link_el = article.locator("xpath=..").first # Parent is usually the link
                    link = await link_el.get_attribute("href")
                    
                    if not link:
                         # Try searching strictly for 'a' tag if parent method fails
                         link_el = article.locator("a").first
                         link = await link_el.get_attribute("href")

                    if title and link:
                        items.append({
                            "title": title.strip(),
                            "short_description": "Men's Health Article",
                            "sub_category": "General Fitness",
                            "source_url": link if link.startswith("http") else f"https://www.menshealth.com{link}",
                            "author": "Men's Health"
                        })
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error scraping Men's Health: {e}")

        return items
