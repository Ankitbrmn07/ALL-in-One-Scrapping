from scraper.core.base_scraper import BaseScraper
from typing import List, Dict

class BBCScraper(BaseScraper):
    CATEGORY = "Politics"
    BASE_URL = "https://www.bbc.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        # BBC structure changes often. 
        # Common pattern: items in a grid with data-testid="card-headline" or similar.
        
        # New BBC Homepage structure often uses <h2 data-testid="card-headline">
        headlines = await self.page.locator('[data-testid="card-headline"]').all()
        
        for hl in headlines:
            try:
                title = await hl.inner_text()
                # The parent 'a' tag usually holds the link. 
                # Sometimes the headline itself is inside the 'a', or the 'a' wraps the card.
                # Let's try finding the closest 'a' ancestor or child.
                
                # Check if hl is inside an 'a' or has an 'a' inside
                link_element = hl.locator("xpath=ancestor::a").first
                if await link_element.count() == 0:
                     link_element = hl.locator("xpath=..").locator("a").first
                
                if await link_element.count() == 0:
                    continue

                link = await link_element.get_attribute("href")
                if link and not link.startswith("http"):
                    link = f"https://www.bbc.com{link}"
                
                # Description often in a sibling 'p' with data-testid="card-description"
                # This is tricky without a solid relative locator strategy universally, 
                # but we can try to look up to the card container.
                summary = ""
                card = hl.locator("xpath=ancestor::div[@data-testid='card-text-wrapper']").first
                if await card.count() > 0:
                     desc_el = card.locator('[data-testid="card-description"]').first
                     if await desc_el.count() > 0:
                         summary = await desc_el.inner_text()

                items.append({
                    "title": title,
                    "short_description": summary,
                    "sub_category": "News",
                    "source_url": link,
                    "author": "BBC News"
                })
            except Exception:
                continue
                
        return items
