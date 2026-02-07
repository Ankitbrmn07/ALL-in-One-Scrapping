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

import json
import hashlib

class BusinessInsiderScraper(BaseScraper):
    CATEGORY = "business"
    BASE_URL = "https://www.businessinsider.com/latest"
    STATE_FILE = "data/business/state_bi123.json"

    def __init__(self, page: Page):
        super().__init__(page)
        self.scraped_urls = self.resume_state_manager()
        self.all_data = []

    def resume_state_manager(self) -> set:
        """Loads previously scraped URLs to avoid duplication."""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, 'r') as f:
                    state = json.load(f)
                    return set(state.get("scraped_urls", []))
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        return set()

    def persist_state(self):
        """Saves current state to file."""
        os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
        with open(self.STATE_FILE, 'w') as f:
            json.dump({"scraped_urls": list(self.scraped_urls)}, f)

    async def fetch_listing_links(self) -> List[str]:
        """Identifies all article links on the current page."""
        """Identifies all article links on the current page."""
        logger.info("BusinessInsider: Fetching listing links...")
        
        # Scroll to bottom to trigger any lazy loading
        # Increased to 10 scrolls to try and catch 100+ items if infinite scroll
        for _ in range(10):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            
        # Main story links often in h2/h3 or river-item
        article_locators = await self.page.locator("h2 a, h3 a, .river-item__title a, a[data-analytics-module='river_item'], .news-stream-item a").all()
        urls = []
        for loc in article_locators:
            href = await loc.get_attribute("href")
            if not href: continue
            
            full_url = href if href.startswith("http") else f"https://www.businessinsider.com{href}"
            # Filter for actual articles
            if "businessinsider.com/" in full_url and not any(x in full_url for x in ["/author/", "/category/", "/newsletter/"]):
                if full_url not in urls:
                    urls.append(full_url)
        return urls

    def deduplicate_records(self, urls: List[str]) -> List[str]:
        """Filters out already scraped URLs."""
        new_urls = [u for u in urls if u not in self.scraped_urls]
        logger.info(f"BusinessInsider: {len(new_urls)} new articles found out of {len(urls)} total.")
        return new_urls

    async def scrape_article_details(self, url: str) -> Dict:
        """Scrapes full details for a single article into the 28-field schema."""
        logger.info(f"BusinessInsider: Scraping details for {url}")
        try:
            print(f"DEBUG: Scraping {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("DEBUG: Page loaded")
            await asyncio.sleep(random.uniform(2, 4))
            
            # Extract basic data
            h1_count = await self.page.locator("h1").count()
            print(f"DEBUG: h1_count: {h1_count}")
            title = "N/A"
            if h1_count > 0:
                title = await self.page.locator("h1").first.inner_text()
            print(f"DEBUG: title: {title}")
            
            # Try broad set of selectors for content
            content_selectors = [
                ".article-body-text p",
                ".premium-content p",
                ".content-lock-content p",
                ".article-body p",
                "article p",
                ".article-content p",
                "main p",
                "div[data-component='article-body'] p"
            ]
            
            content_nodes = []
            for selector in content_selectors:
                nodes = await self.page.locator(selector).all()
                if nodes:
                    content_nodes = nodes
                    print(f"DEBUG: Found {len(nodes)} nodes using selector: {selector}")
                    break
            
            if not content_nodes:
                # Last resort: all paragraphs in main article
                content_nodes = await self.page.locator("p").all()
                print(f"DEBUG: Fallback to all p tags: {len(content_nodes)}")
            
            content_list = []
            for n in content_nodes:
                try:
                    text = await n.inner_text()
                    if len(text) > 30:
                        content_list.append(text)
                except Exception as node_e:
                    print(f"DEBUG: node error: {node_e}")
            content_text = "\n".join(content_list)
            
            # Meta fields
            meta_desc_loc = self.page.locator('meta[name="description"]')
            meta_desc = ""
            if await meta_desc_loc.count() > 0:
                meta_desc = await meta_desc_loc.get_attribute("content")
            
            og_image_loc = self.page.locator('meta[property="og:image"]')
            og_image = ""
            if await og_image_loc.count() > 0:
                og_image = await og_image_loc.get_attribute("content")
            
            canonical_loc = self.page.locator('link[rel="canonical"]')
            canonical = url
            if await canonical_loc.count() > 0:
                full_canonical = await canonical_loc.get_attribute("href")
                if full_canonical: canonical = full_canonical
            
            # Images
            img_nodes = await self.page.locator("article img, .article-body img").all()
            all_images = []
            for img in img_nodes:
                src = await img.get_attribute("src")
                if src and "http" in src: all_images.append(src)
            all_images = list(set(all_images))
            
            author_loc = self.page.locator(".author-name")
            author = "Business Insider"
            if await author_loc.count() > 0:
                author_text = await author_loc.first.inner_text()
                if author_text: author = author_text
            
            now = datetime.now().isoformat()
            
            # 28-field Schema
            item = {
                "id": hashlib.md5(url.encode()).hexdigest(),
                "run_id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "row_id": len(self.all_data) + 1,
                "title": title.strip(),
                "description": meta_desc.strip() if meta_desc else "",
                "source": author.strip(),
                "category": self.CATEGORY,
                "link": url,
                "image_url": og_image or (all_images[0] if all_images else ""),
                "status": "published",
                "scheduled_at": "",
                "created_at": now,
                "updated_at": now,
                "likes": 0,
                "content": content_text.strip(),
                "slug": title.lower().replace(" ", "-").replace("'", "").replace("\"", "")[:50],
                "excerpt": content_text[:200].strip() + "...",
                "meta_title": title.strip(),
                "meta_description": meta_desc.strip() if meta_desc else "",
                "meta_keywords": "",
                "canonical_url": canonical,
                "og_title": title.strip(),
                "og_description": meta_desc.strip() if meta_desc else "",
                "og_image": og_image if og_image else "",
                "focus_keyword": "",
                "is_indexable": True,
                "is_followable": True,
                "images": ",".join(all_images)
            }
            return item
        except Exception as e:
            print(f"DEBUG: Error in scrape_article_details: {e}")
            logger.error(f"Failed to scrape {url}: {e}")
            return None

    async def handle_pagination(self) -> bool:
        """Navigates to the next page if possible."""
        # Try various selectors for Next/Load More
        selectors = [
            "a[rel='next']", 
            ".load-more-button", 
            "button:has-text('Load More')",
            "span:has-text('Load More')",
            ".pagination__next",
            "nav a:has-text('Next')"
        ]
        
        for sel in selectors:
            btn = self.page.locator(sel)
            if await btn.count() > 0:
                logger.info(f"BusinessInsider: Found pagination button: {sel}")
                try:
                    await btn.first.click()
                    await asyncio.sleep(4)
                    return True
                except:
                    continue
                    
        return False

    def save_to_csv(self, data: List[Dict]):
        """Persists data to CSV using the Exporter."""
        from scraper.core.exporter import Exporter
        output_file = "data/business/business_insider_data123.csv"
        Exporter.to_csv(data, output_file)

    async def scrape(self) -> List[Dict]:
        """Orchestrates the modular scraping process."""
        await self.page.goto(self.BASE_URL, wait_until="domcontentloaded")
        page_count = 1
        
        # Target 200+ items or max 50 pages to ensure we get >100
        while len(self.all_data) < 200 and page_count <= 50:
            links = await self.fetch_listing_links()
            new_links = self.deduplicate_records(links)
            
            for url in new_links:
                detail = await self.scrape_article_details(url)
                if detail:
                    self.all_data.append(detail)
                    self.scraped_urls.add(url)
                    self.persist_state()
                
            if not await self.handle_pagination():
                break
            page_count += 1
            
        self.save_to_csv(self.all_data)
        logger.info(f"BusinessInsider: Total scraped: {len(self.all_data)}")
        return self.all_data
