from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ESPNCricinfoScraper(BaseScraper):
    CATEGORY = "Sports"
    BASE_URL = "https://www.espncricinfo.com/"

    async def extract_items(self) -> List[Dict]:
        items = []

        try:
            # Matches / News
            # Based on rendered HTML analysis:
            # Articles seem to be wrapped in 'a' tags that contain 'div.ds-flex.ds-flex-col.ds-mb-4'
            # Or we can look for the headers 'h3.ds-text-header-4' or 'h3.ds-text-body-2'

            # Let's try to grab all anchors that contain a title
            
            # This selector targets the news blocks we saw
            article_containers = await self.page.locator("a:has(div.ds-flex.ds-flex-col)").all()
            
            for container in article_containers[:15]:
                try:
                    # Title is usually in an h3 or inside the div
                    title_el = container.locator("h3").first
                    if not await title_el.count():
                         # Fallback for other layouts
                         title_el = container.locator(".ds-text-title-s, .ds-text-header-4, .ds-text-body-2").first

                    if await title_el.count() > 0:
                        name = await title_el.inner_text()
                        link = await container.get_attribute("href")
                        
                        # Image
                        img_el = container.locator("img").first
                        img_src = ""
                        if await img_el.count() > 0:
                             img_src = await img_el.get_attribute("src")

                        # Handle relative links
                        if link and not link.startswith("http"):
                            link = f"https://www.espncricinfo.com{link}"

                        if name and len(name) > 10: # Filter out small generic links
                            items.append({
                                "title": name.strip(),
                                "short_description": "Cricket News",
                                "sub_category": "Cricket",
                                "source_url": link,
                                "author": "ESPNcricinfo",
                                "image_url": img_src
                            })
                except Exception as e:
                    # logger.warning(f"Error scraping item: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error scraping ESPNCricinfo: {e}")

        return items
