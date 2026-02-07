from scraper.core.base_scraper import BaseScraper
import asyncio
import logging
import random
import re
import csv
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class PeopleScraper(BaseScraper):
    CATEGORY = "entertainment"
    BASE_URL = "https://people.com/"
    STATE_FILE = "data/entertainment/state_people.json"

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
        """Identifies article links on the People.com homepage/listing page."""
        logger.info("People: Fetching listing links...")
        # People.com uses cards for articles
        article_locators = await self.page.locator("a.card, a.mntl-card-list-items, .card-list__list a, article a").all()
        urls = []
        for loc in article_locators:
            href = await loc.get_attribute("href")
            if not href: continue
            
            full_url = href if href.startswith("http") else f"https://people.com{href}"
            # Filter for meaningful article links
            if "people.com/" in full_url and not any(x in full_url for x in ["/search?", "/author/"]):
                if full_url not in urls:
                    urls.append(full_url)
        return urls

    def deduplicate_records(self, urls: List[str]) -> List[str]:
        """Filters out already scraped URLs."""
        new_urls = [u for u in urls if u not in self.scraped_urls]
        logger.info(f"People: {len(new_urls)} new articles found out of {len(urls)} total.")
        return new_urls

    async def scrape_article_details(self, url: str) -> Dict:
        """Scrapes full details for a single People.com article into the 28-field schema."""
        logger.info(f"People: Scraping details for {url}")
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(2, 5))
            
            # Extract basic data
            title_node = self.page.locator("h1").first
            title = await title_node.inner_text() if await title_node.count() > 0 else "N/A"
            
            # Content extraction with multiple selectors
            selectors = [
                ".paragraph", 
                "p", 
                ".article-content p", 
                ".mntl-sc-block-reveal__content p",
                ".article-body p"
            ]
            
            content_nodes = []
            for sel in selectors:
                found = await self.page.locator(sel).all()
                if len(found) > 3: # Prefer selectors that give more content
                    content_nodes = found
                    break
            
            if not content_nodes:
                content_nodes = await self.page.locator("p").all()
                
            content_list = []
            for n in content_nodes:
                try:
                    text = await n.inner_text()
                    if len(text) > 30:
                        content_list.append(text)
                except:
                    continue
            content_text = "\n".join(content_list)
            
            # Meta fields (SEO & OpenGraph)
            meta_desc_node = self.page.locator('meta[name="description"]')
            meta_desc = ""
            if await meta_desc_node.count() > 0:
                meta_desc = await meta_desc_node.get_attribute("content")
            
            og_image_node = self.page.locator('meta[property="og:image"]')
            og_image = ""
            if await og_image_node.count() > 0:
                og_image = await og_image_node.get_attribute("content")
                
            canonical_node = self.page.locator('link[rel="canonical"]')
            canonical = url
            if await canonical_node.count() > 0:
                full_canonical = await canonical_node.get_attribute("href")
                if full_canonical: canonical = full_canonical
            
            meta_keywords_node = self.page.locator('meta[name="keywords"]')
            meta_keywords = ""
            if await meta_keywords_node.count() > 0:
                meta_keywords = await meta_keywords_node.get_attribute("content")
            
            # Images
            img_nodes = await self.page.locator("img").all()
            all_images = []
            for img in img_nodes:
                src = await img.get_attribute("src")
                if src and "http" in src and "avatar" not in src.lower():
                    all_images.append(src)
            all_images = list(set(all_images))
            
            # Breadcrumb for category
            category = self.CATEGORY
            breadcrumb_node = self.page.locator(".mntl-breadcrumb").first
            if await breadcrumb_node.count() > 0:
                category = await breadcrumb_node.inner_text()
            
            author_node = self.page.locator(".mntl-attribution__item-name")
            author = "People Staff"
            if await author_node.count() > 0:
                author_text = await author_node.first.inner_text()
                if author_text: author = author_text
            
            now = datetime.now().isoformat()
            
            # 28-field Schema
            item = {
                "id": hashlib.md5(url.encode()).hexdigest(),
                "run_id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "row_id": len(self.all_data) + 1,
                "title": title.strip(),
                "description": meta_desc.strip(),
                "source": author.strip(),
                "category": category.strip(),
                "link": url,
                "image_url": og_image or (all_images[0] if all_images else ""),
                "status": "published",
                "scheduled_at": "",
                "created_at": now,
                "updated_at": now,
                "likes": 0,
                "content": content_text.strip(),
                "slug": title.lower().replace(" ", "-").replace("'", "").replace("\"", "")[:50],
                "excerpt": content_text[:250].strip() + "...",
                "meta_title": title.strip(),
                "meta_description": meta_desc.strip(),
                "meta_keywords": meta_keywords,
                "canonical_url": canonical,
                "og_title": title.strip(),
                "og_description": meta_desc.strip(),
                "og_image": og_image,
                "focus_keyword": "",
                "is_indexable": True,
                "is_followable": True,
                "images": ",".join(all_images)
            }
            return item
        except Exception as e:
            logger.error(f"People: Failed to scrape {url}: {e}")
            return None

    async def handle_pagination(self) -> bool:
        """Handles pagination for People.com (often has 'Next' or Load More)."""
        next_button = self.page.locator("a[rel='next'], .load-more-button")
        if await next_button.count() > 0:
            logger.info("People: Moving to next page...")
            await next_button.first.click()
            await asyncio.sleep(4)
            return True
        return False

    def save_to_csv(self, data: List[Dict]):
        """Persists data to CSV using the standardized Exporter."""
        from scraper.core.exporter import Exporter
        output_file = "data/business/people_data.csv"
        Exporter.to_csv(data, output_file)

    async def scrape(self) -> List[Dict]:
        """Main entry point for the modular scraping flow."""
        await self.page.goto(self.BASE_URL, wait_until="domcontentloaded")
        page_count = 1
        
        while len(self.all_data) < 150 and page_count <= 25: # Restricted for testing/performance
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
        logger.info(f"People: Total articles scraped: {len(self.all_data)}")
        return self.all_data
