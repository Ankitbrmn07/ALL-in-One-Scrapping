from scraper.core.base_scraper import BaseScraper
import asyncio
import logging
import random
import re
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class BusinessInsiderScraper(BaseScraper):
    CATEGORY = "business"
    BASE_URL = "https://www.businessinsider.com/"

    async def extract_items(self) -> List[Dict]:
        """
        Main logic to identify and extract items from Business Insider.
        Format requested: Serial, Title, Type, Amenities, Price, Address, Images, Description, Summary, Source, Extra.
        """
        scraped_data = []
        serial_counter = 1
        page_num = 1
        
        try:
            while True:
                logger.info(f"BusinessInsider: Scraping page {page_num}...")
                
                # Detect all visible Post/Article links
                # Based on inspection, articles are often in <h3> tags with links
                article_locators = await self.page.locator("h2 a, h3 a, .river-item__title a").all()
                logger.info(f"BusinessInsider: Total potential link locators found: {len(article_locators)}")
                
                # Filter out non-article links and get unique URLs
                article_urls = []
                for loc in article_locators:
                    href = await loc.get_attribute("href")
                    if not href:
                        continue
                        
                    # Handle relative URLs
                    full_url = href
                    if href.startswith("/"):
                        full_url = f"https://www.businessinsider.com{href}"
                    
                    if full_url.startswith("https://www.businessinsider.com/") and \
                       "/author/" not in full_url and \
                       "/category/" not in full_url and \
                       "businessinsider.com/" in full_url:
                        if full_url not in article_urls:
                            article_urls.append(full_url)
                
                logger.info(f"BusinessInsider: Found {len(article_urls)} unique article links on page {page_num}.")
                
                if not article_urls:
                    logger.warning(f"BusinessInsider: No article links found on page {page_num}. Trying alternative selector...")
                    # Alternative: a tags with specific classes or structures
                    alt_locators = await self.page.locator("a[data-analytics-module='river_item']").all()
                    for loc in alt_locators:
                        href = await loc.get_attribute("href")
                        if href:
                            full_url = href if href.startswith("http") else f"https://www.businessinsider.com{href}"
                            if full_url not in article_urls:
                                article_urls.append(full_url)
                    logger.info(f"BusinessInsider: Total unique links after alternative: {len(article_urls)}")

                if not article_urls:
                    logger.error(f"BusinessInsider: Still no links found on page {page_num}. Stopping.")
                    break

                for url in article_urls:
                    try:
                        logger.info(f"BusinessInsider: Scraping article {serial_counter}: {url}")
                        
                        # Random delay to avoid detection
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        # Go to article detail page
                        await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        
                        # Wait for some content
                        await self.page.wait_for_selector("h1", timeout=10000)
                        
                        # Extract data
                        title = await self.page.locator("h1").first.inner_text() if await self.page.locator("h1").count() > 0 else "N/A"
                        
                        # Description/Content
                        content_locators = await self.page.locator(".content-lock-content p, .article-body p, .article-content p").all()
                        description = " ".join([await p.inner_text() for p in content_locators])
                        
                        # Summary (BI often has 'Summary' or bullet points at the top)
                        summary_locators = await self.page.locator(".summary-list li, .article-summary li").all()
                        summary = " ".join([await s.inner_text() for s in summary_locators])
                        if not summary:
                            summary = description[:200] + "..." if description else "N/A"
                            
                        # Images (Extract multiple)
                        image_locators = await self.page.locator("img.article-image, .image-figure img, .article-body img").all()
                        images_list = []
                        for img in image_locators:
                            src = await img.get_attribute("src")
                            if src and "http" in src:
                                images_list.append(src)
                        images_str = ",".join(list(set(images_list))) if images_list else "N/A"
                        
                        # Map other fields as requested (using placeholders if not applicable but following structure)
                        # Type (Property Type) -> Inferred from category or keywords
                        item_type = "Article"
                        if "real estate" in description.lower() or "house" in description.lower() or "/home/" in url:
                            item_type = "Real Estate"
                            
                        # Price (Canadian Dollar price only, numeric + CAD)
                        # Heuristic: search for price in text
                        price = "N/A"
                        price_match = re.search(r'(\$[\d,]+(\.\d+)?)\s*(CAD|Canadian Dollars)?', description)
                        if price_match:
                            price = price_match.group(1) + " CAD"
                        
                        # Address
                        address = "N/A"
                        # BI articles don't always have addresses unless it's a profile
                        
                        # Amenities
                        amenities = "N/A"
                        
                        # Extra metadata
                        extra = {
                            "author": await self.page.locator(".author-name").first.inner_text() if await self.page.locator(".author-name").count() > 0 else "Business Insider",
                            "published_date": await self.page.locator("time").first.get_attribute("datetime") if await self.page.locator("time").count() > 0 else "N/A"
                        }

                        item = {
                            "Serial": serial_counter,
                            "Title": title.strip(),
                            "Type": item_type,
                            "Amenities": amenities,
                            "Price": price,
                            "Address": address,
                            "Images": images_str,
                            "Description": description.strip(),
                            "Summary": summary.strip(),
                            "Source": url,
                            "Extra": str(extra)
                        }
                        
                        scraped_data.append(item)
                        serial_counter += 1
                        
                        # Navigate BACK to the homepage (or listings page)
                        # Instead of go back, we can just navigate to the next URL or use back
                        await self.page.go_back(wait_until="domcontentloaded")
                        await asyncio.sleep(random.uniform(1, 2))
                        
                    except Exception as e:
                        logger.error(f"BusinessInsider: Failed to scrape {url}: {e}")
                        # Ensure we try to go back even on failure
                        try:
                            await self.page.goto(self.BASE_URL, wait_until="domcontentloaded")
                        except:
                            pass
                        continue

                # Pagination
                # Business Insider usually has infinite scroll or "More" button on home
                # If we are on a specific category page, there might be ?p=2
                # For homepage, we might just stop after one round or look for "Next"
                
                # Check for "Next Page" or "Load More"
                next_button = self.page.locator("a[rel='next'], .load-more-button, .pagination-next")
                if await next_button.count() > 0:
                    logger.info("BusinessInsider: Moving to next page...")
                    await next_button.first.click()
                    await self.page.wait_for_load_state('domcontentloaded')
                    page_num += 1
                    await asyncio.sleep(3)
                else:
                    # Fallback pagination via URL if applicable
                    # For homepage it's tricky, usually limited to current view
                    logger.info("BusinessInsider: No pagination found. Finishing.")
                    break
                
                # Safety break
                if page_num > 5: 
                    break

            # Store all collected data in a CSV file with proper headers
            self.export_to_csv(scraped_data)
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"BusinessInsider: Scraper crashed: {e}")
            return scraped_data

    def export_to_csv(self, data: List[Dict]):
        if not data:
            return
        
        output_dir = "data/business"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/business_insider_data.csv"
        
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        
        logger.info(f"BusinessInsider: Data exported to {filename}")

    async def scrape(self) -> List[Dict]:
        """
        Overriding base scrape to handle the custom flow.
        """
        try:
            await self.page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=60000)
            await self.handle_captcha()
            items = await self.extract_items()
            
            # Standardization (add common fields)
            standardized_items = []
            for item in items:
                item['category'] = self.CATEGORY
                item['website'] = self.BASE_URL
                item['scraped_at'] = datetime.now().isoformat()
                standardized_items.append(item)
            
            self.data = standardized_items
            return self.data
        except Exception as e:
            logger.error(f"Error during Business Insider scraping: {e}")
            return []
