from scraper.core.base_scraper import BaseScraper
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class IMDbScraper(BaseScraper):
    CATEGORY = "Bollywood"
    BASE_URL = "https://www.imdb.com/india/top-rated-indian-movies/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        # Scrape Top Rated Indian Movies
        try:
            # New structure uses ipc-metadata-list__item
            movie_rows = await self.page.locator("li.ipc-metadata-list__item").all()
            
            for row in movie_rows[:15]:
                try:
                    # Title is in a span with data-testid 'rank-list-item-title'
                    # It contains the rank (e.g. "1. ") and the text.
                    title_el = row.locator("span[data-testid='rank-list-item-title']").first
                    
                    # Link might be on the icon or separate. 
                    # We can use the icon link which definitely has the href.
                    link_el = row.locator("a.ipc-metadata-list-item__icon-link").first
                    if not await link_el.count():
                         link_el = row.locator("a[href^='/title/']").first

                    if await title_el.count() > 0:
                        full_title_text = await title_el.inner_text()
                        # Remove rank if present (e.g. "1. 3 Idiots" -> "3 Idiots")
                        parts = full_title_text.split(" ", 1)
                        if len(parts) > 1 and parts[0].replace(".", "").isdigit():
                            title = parts[1]
                        else:
                            title = full_title_text
                            
                        link = await link_el.get_attribute("href")
                        
                        # Rating
                        rating_el = row.locator("span.ipc-rating-star--rating").first
                        rating = await rating_el.inner_text() if await rating_el.count() > 0 else "N/A"

                        # Image
                        img_el = row.locator("img.ipc-image").first
                        img_src = ""
                        if await img_el.count() > 0:
                            img_src = await img_el.get_attribute("src")

                        full_link = f"https://www.imdb.com{link}" if link and link.startswith("/") else link

                        items.append({
                            "title": title.strip(),
                            "short_description": f"Rating: {rating}",
                            "sub_category": "Top Rated Indian Movies",
                            "source_url": full_link,
                            "author": "IMDb",
                            "image_url": img_src
                        })
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error scraping IMDb: {e}")

        return items
