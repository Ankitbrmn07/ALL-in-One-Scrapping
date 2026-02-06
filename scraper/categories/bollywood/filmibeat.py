from scraper.core.base_scraper import BaseScraper
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class FilmiBeatScraper(BaseScraper):
    CATEGORY = "Bollywood"
    BASE_URL = "https://www.filmibeat.com/"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        try:
            # Wait for basic page load (don't wait for networkidle - it times out due to ads/tracking)
            await self.page.wait_for_load_state('domcontentloaded', timeout=10000)
            
            # Give it a moment for initial content to render
            import asyncio
            await asyncio.sleep(3)
            
            # FilmiBeat structure: Try broader selectors
            # Look for any links that might be articles
            article_links = await self.page.locator('a[href*="/bollywood/"], a[href*="/news/"], a[href*="/celeb/"], a[href*="/features/"]').all()
            
            # If specific selectors don't work, get all links in common article containers
            if len(article_links) == 0:
                article_links = await self.page.locator('article a, .news-card a, .story a, div[class*="card"] a').all()
            
            # Fallback: get all links with meaningful titles
            if len(article_links) == 0:
                article_links = await self.page.locator('a').all()
            
            seen_urls = set()
            
            for link_elem in article_links[:50]:  # Check up to 50 links
                try:
                    href = await link_elem.get_attribute('href')
                    if not href or href in seen_urls:
                        continue
                    
                    # Skip non-article links
                    if any(skip in href for skip in ['javascript:', '#', 'mailto:', 'tel:']):
                        continue
                    
                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"{self.BASE_URL.rstrip('/')}{href}"
                    elif not href.startswith('http'):
                        continue
                    
                    # Only keep filmibeat.com URLs
                    if 'filmibeat.com' not in href:
                        continue
                    
                    seen_urls.add(href)
                    
                    # Get title
                    title = await link_elem.inner_text()
                    title = title.strip()
                    
                    # Filter out navigation links, social media, etc.
                    if not title or len(title) < 10 or len(title) > 200:
                        continue
                    
                    if any(skip in title.lower() for skip in ['home', 'login', 'sign up', 'subscribe', 'follow us']):
                        continue
                    
                    items.append({
                        "title": title,
                        "short_description": "",
                        "sub_category": "Entertainment",
                        "source_url": href,
                        "author": "FilmiBeat",
                        "published_date": ""
                    })
                    
                    # Stop once we have enough
                    if len(items) >= 20:
                        break
                    
                except Exception as e:
                    logger.debug(f"Error extracting article: {e}")
                    continue
            
            logger.info(f"FilmiBeat: Found {len(items)} articles")
            
        except Exception as e:
            logger.error(f"Error in FilmiBeat scraper: {e}")
            import traceback
            traceback.print_exc()
        
        return items
