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
            # IMDb's structure often involves a list of `li` items in a `ipc-metadata-list`
            movie_rows = await self.page.locator(".ipc-metadata-list li.ipc-metadata-list-summary-item").all()
            
            for row in movie_rows[:15]:
                try:
                    title_el = row.locator("h3.ipc-title__text").first
                    link_el = row.locator("a.ipc-title-link-wrapper").first
                    
                    if await title_el.count() > 0:
                        title = await title_el.inner_text()
                        link = await link_el.get_attribute("href")
                        
                        # Metadata (Year, Rating)
                        metadata_items = row.locator(".cli-title-metadata span").all()
                        metadata_text = []
                        for meta in await metadata_items:
                            metadata_text.append(await meta.inner_text())
                        
                        rating_el = row.locator(".ipc-rating-star").first
                        rating = await rating_el.inner_text() if await rating_el.count() > 0 else "N/A"

                        full_link = f"https://www.imdb.com{link}" if link.startswith("/") else link

                        items.append({
                            "title": title.strip(),
                            "short_description": f"Rating: {rating}, Info: {' | '.join(metadata_text)}",
                            "sub_category": "Top Rated Indian Movies",
                            "source_url": full_link,
                            "author": "IMDb"
                        })
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error scraping IMDb: {e}")

        return items
