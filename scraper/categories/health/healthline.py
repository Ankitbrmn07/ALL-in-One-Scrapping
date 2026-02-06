from scraper.core.base_scraper import BaseScraper
from typing import List, Dict

class HealthlineScraper(BaseScraper):
    CATEGORY = "Health"
    BASE_URL = "https://www.healthline.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # Healthline Home often has a "css-..." class mess, but standard semantic tags usually exist.
        # Look for article links usually in a list or grid.
        
        # Strategy: Look for standard article cards.
        # Often links under `a` tags which contain `h2` or `h3`.
        
        article_links = await self.page.locator("a[href*='/health/'], a[href*='/nutrition/']").all()
        
        # Deduplicate by URL
        seen_urls = set()
        
        for a in article_links[:20]: # Limit to first 20 for homepage scrape
            try:
                link = await a.get_attribute("href")
                if not link or link in seen_urls:
                    continue
                    
                if not link.startswith("http"):
                    link = f"https://www.healthline.com{link}"

                seen_urls.add(link)
                
                # Try to get title from text or child header
                title = await a.inner_text()
                if not title.strip():
                    # Check for h2/h3 inside
                    h2 = a.locator("h2, h3").first
                    if await h2.count() > 0:
                        title = await h2.inner_text()
                
                if not title.strip():
                    continue

                # Summary is hard to get from just the link on some layouts, 
                # but sometimes it's a sibling. 
                # For this robust heuristic, we just take title and link.
                
                items.append({
                    "title": title,
                    "short_description": "",
                    "sub_category": "Health Article",
                    "source_url": link,
                    "author": "Healthline"
                })
            except:
                pass

        return items
