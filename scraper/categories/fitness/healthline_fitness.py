from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class HealthlineFitnessScraper(BaseScraper):
    CATEGORY = "Fitness"
    BASE_URL = "https://www.healthline.com/fitness"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # Healthline Fitness specific scraping
        # Structure is often similar to main Healthline but focused on fitness topics
        try:
           # 1. Feature / Hero
            hero_items = await self.page.locator(".css-1r1y02, .css-7813r8").all() # Typical Healthline hero class patterns (randomized often, so using generic fallback)
            if not hero_items:
                hero_items = await self.page.locator("main article").all()

            for item in hero_items[:3]:
                try:
                    title_el = item.locator("h1, h2, h3").first
                    link_el = item.locator("a").first
                    
                    if await title_el.count() > 0 and await link_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await link_el.get_attribute("href")
                        
                        items.append({
                            "title": title.strip(),
                            "short_description": "Fitness Feature",
                            "sub_category": "Fitness Guide",
                            "source_url": link if link.startswith("http") else f"https://www.healthline.com{link}",
                            "author": "Healthline"
                        })
                except:
                    continue
            
            # 2. Feed Items
            feed_items = await self.page.locator(".css-1p2q3t4, .css-1n7b1j2").all() # New feed patterns
            if not feed_items:
                 feed_items = await self.page.locator("li a").all() # Fallback

            for item in feed_items[:10]:
                 try:
                    link = await item.get_attribute("href")
                    if link and "/fitness" in link:
                         title_el = item.locator("h2, div").first
                         if await title_el.count() > 0:
                             title = await title_el.inner_text()
                         else:
                             title = await item.inner_text()
                        
                         if len(title) > 10: # Filter short nav links
                             items.append({
                                "title": title.strip(),
                                "short_description": "Fitness Article",
                                "sub_category": "Education",
                                "source_url": link if link.startswith("http") else f"https://www.healthline.com{link}",
                                "author": "Healthline"
                             })
                 except:
                     continue
                     
        except Exception as e:
            logger.warning(f"Error scraping Healthline Fitness: {e}")

        return items
