from scraper.core.base_scraper import BaseScraper
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class FashionUnitedScraper(BaseScraper):
    CATEGORY = "Fashion"
    BASE_URL = "https://fashionunited.in/news/fashion"

    async def extract_items(self) -> List[Dict]:
        items = []
        
        try:
            # Wait for content
            await self.page.wait_for_load_state('domcontentloaded')
            
            # Method 1: Try extracting from Next.js data (more reliable)
            try:
                # Get the JSON data from the script tag
                next_data_script = self.page.locator("script#__NEXT_DATA__")
                if await next_data_script.count() > 0:
                    json_text = await next_data_script.inner_text()
                    data = json.loads(json_text)
                    
                    # Traverse to find articles in apolloState
                    apollo_state = data.get('props', {}).get('pageProps', {}).get('apolloState', {})
                    
                    for key, node in apollo_state.items():
                        if key.startswith('LocalNewsArticle:') and isinstance(node, dict):
                            title = node.get('title', '')
                            summary = node.get('summary') or node.get('description', '')
                            slug = node.get('slug', '')
                            # Construct URL
                            path = node.get('path', '')
                            url = f"https://fashionunited.in{path}" if path else ""
                            
                            # Get image
                            image_url = ""
                            images = node.get('imageUrls')
                            if images and isinstance(images, list) and len(images) > 0:
                                image_url = images[0]
                                
                            if title and url:
                                items.append({
                                    "title": title.strip(),
                                    "short_description": summary.strip(),
                                    "sub_category": "Fashion News",
                                    "source_url": url,
                                    "author": "Fashion United",
                                    "image_url": image_url,
                                    "published_date": node.get('insertedAt', '')
                                })
                    
                    if items:
                        logger.info(f"FashionUnited: Extracted {len(items)} items from JSON.")
                        return items
            except Exception as e:
                logger.warning(f"FashionUnited: JSON extraction failed: {e}")

            # Method 2: Fallback to CSS selectors (updated for current layout)
            logger.info("FashionUnited: Falling back to CSS selectors.")
            articles = await self.page.locator(".MuiGridLegacy-item").all()
            
            for article in articles:
                try:
                    # Look for title inside h2
                    title_el = article.locator("h2").first
                    if await title_el.count() == 0:
                        continue
                        
                    title = await title_el.inner_text()
                    
                    # Find link
                    link_el = article.locator("a").first
                    link = await link_el.get_attribute("href")
                    if not link:
                        continue
                        
                    # Fix relative links
                    if not link.startswith("http"):
                        link = f"https://fashionunited.in{link}"
                        
                    # Summary
                    summary = ""
                    summary_el = article.locator("p").first
                    if await summary_el.count() > 0:
                        summary = await summary_el.inner_text()
                        
                    items.append({
                        "title": title.strip(),
                        "short_description": summary.strip(),
                        "sub_category": "Fashion",
                        "source_url": link,
                        "author": "Fashion United",
                        "image_url": ""
                    })
                    
                    if len(items) >= 20:
                        break
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Fashion United: {e}")

        logger.info(f"FashionUnited: Scraped {len(items)} items.")
        return items
