import logging
import asyncio
import re
import hashlib
from datetime import datetime
from playwright.async_api import Page
from bs4 import BeautifulSoup

class ZoloExtractor:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger("ZoloExtractor")

    # --- Helpers Ported from Reference ---
    def generate_hash_id(self, title, address, price):
        """Generate robust hash ID using normalized address and price."""
        norm_addr = address.lower()
        norm_addr = re.sub(r'[^\w\s]', '', norm_addr)
        norm_addr = re.sub(r'\s+', ' ', norm_addr).strip()
        raw = f"{norm_addr}_{str(price)}".encode('utf-8')
        return hashlib.md5(raw).hexdigest()

    def extract_location(self, address):
        """Dynamically extract City, State, Country from address string."""
        city, state, country = "Unknown", "Unknown", "Unknown"
        if not address or address == "N/A":
            return city, state, country

        parts = [p.strip() for p in address.split(',')]
        if len(parts) >= 3:
            if "canada" in parts[-1].lower() or "usa" in parts[-1].lower():
                 country = parts[-1]
                 state = parts[-2]
                 city = parts[-3]
            else:
                 state = parts[-1] 
                 city = parts[-2]
                 country = "Canada"
        elif len(parts) == 2:
            city = parts[0]
            state = parts[1]
        
        city = re.sub(r'\d+', '', city).strip()
        return city, state, country

    async def smart_scroll(self, max_scrolls=5):
        """Playwright implementation of smart scroll."""
        self.logger.info("Starting smart scroll sequence...")
        for i in range(max_scrolls):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(2000) # Random pause simulation
            new_height = await self.page.evaluate("document.body.scrollHeight")
            # In a real infinite scroll, we'd check if height changed, but for Zolo paginated map/list
            # sometimes it handles both. We'll just scroll a bit to trigger lazy loads.

    # --- Extraction ---
    async def extract(self):
        self.logger.info("Starting Zolo extraction (Robust Version)...")
        
        # 1. Wait for listings
        try:
            await self.page.wait_for_selector("article.card-listing, div.card-listing, div[class*='listing-card']", timeout=30000)
            self.logger.info("Listings loaded.")
        except Exception as e:
            self.logger.warning(f"Timeout waiting for listings: {e}")
            
        # 2. Smart Scroll to load lazy images/content
        await self.smart_scroll(max_scrolls=3)

        # 3. Parse Content
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        cards = soup.select("article.card-listing, div.card-listing, div[class*='listing-card']")
        self.logger.info(f"Found {len(cards)} listing cards.")
        
        extracted_data = []
        
        for i, card in enumerate(cards):
            try:
                # Basic Extraction (Ported Logic)
                
                # Source URL
                link_tag = card.find('a', href=True)
                source_url = "https://www.zolo.ca" + link_tag['href'] if link_tag and not link_tag['href'].startswith('http') else (link_tag['href'] if link_tag else self.page.url)

                # Address
                address = "N/A"
                addr_tag = card.select_one(".address, span[itemprop='streetAddress'], h3")
                if addr_tag:
                    address = addr_tag.get_text(strip=True)
                
                # Price
                price_text = "0"
                price_tag = card.select_one("span[itemprop='price'], .price")
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                price_clean = re.sub(r'[^\d.]', '', price_text)
                price_val = float(price_clean) if price_clean else 0.0

                # Location
                city, state, country = self.extract_location(address)
                
                # Attributes
                amenities = []
                info_tags = card.select("ul.card-listing--values li, .features li")
                for tag in info_tags:
                    amenities.append(tag.get_text(strip=True))

                # Images (Card)
                images = []
                img_tag = card.find('img')
                if img_tag:
                    src = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-srcset')
                    if src and "http" in src:
                         images.append(src.split()[0]) # handle srcset 'url 480w' format
                
                # Title & Hash
                title = address if address != "N/A" else f"Zolo Listing #{i}"
                hash_id = self.generate_hash_id(title, address, price_val)
                serial_no = f"ZO-{hash_id[:6]}"
                
                # Prepare Item (Matching Reference Schema logic)
                item = {
                    "serial": serial_no,
                    "title": title,
                    "property_type": "Residential", # Default
                    "amenities": amenities,     # List, will join later
                    "price": price_text,        # Keep original text format for CSV
                    "address": address,
                    "images": images,           # List
                    "description": f"Zolo listing in {city}", # Placeholder until detail
                    "summary": f"For sale: {price_text}",     # AI Summary placeholder
                    "source": "Zolo.ca",
                    
                    # Internal/Extra
                    "source_url": source_url,
                    "city": city,
                    "extra": {
                        "hash_id": hash_id,
                        "scraped_at": str(datetime.now())
                    }
                }
                
                extracted_data.append(item)
                
            except Exception as e:
                self.logger.error(f"Error parsing card {i}: {e}")
                continue

        # 4. Detail Page Extraction (Resurrected from previous step, integrated)
        self.logger.info(f"Visiting {len(extracted_data)} listing pages for details...")
        for item in extracted_data:
            url = item.get('source_url')
            if not url or "zolo.ca" not in url: continue
            
            try:
                await self.page.goto(url, timeout=30000)
                await self.page.wait_for_load_state("domcontentloaded")
                
                # Description
                desc_el = await self.page.query_selector(".description, [itemprop='description'], section.listing-description")
                if desc_el:
                    item['description'] = await desc_el.inner_text()
                
                # Amenities (Detailed)
                # Using robust check from recent analysis
                am_els = await self.page.query_selector_all(".amenities li, .listing-amenities li, ul.list-columns li")
                detailed_amenities = []
                for am in am_els:
                    detailed_amenities.append(await am.inner_text())
                if detailed_amenities:
                    item['amenities'] = list(set(item['amenities'] + detailed_amenities))

                # Images (Gallery)
                img_els = await self.page.query_selector_all("img.photo, .gallery-image img")
                for img in img_els:
                    src = await img.get_attribute('src')
                    if src and "http" in src: item['images'].append(src)
                item['images'] = list(set(item['images']))

                await asyncio.sleep(1) # Polite pause

            except Exception as e:
                 self.logger.error(f"Detail extract error {url}: {e}")

        # Post-Processing for CSV Compatibility
        # Reference CSV: Serial, Title, Type, Amenities, Price, Address, Images, Description, Summary, Source
        # We need to flatten lists
        final_data = []
        for item in extracted_data:
            final_data.append({
                "serial": item['serial'],
                "title": item['title'],
                "property_type": item['property_type'], # 'Type' in CSV
                "amenities": ", ".join(item['amenities']),
                "price": item['price'],
                "address": item['address'],
                "images": item['images'][0] if item['images'] else "N/A", # Reference usually takes main image
                "description": item['description'],
                "summary": item['summary'],
                "source": item['source']
            })

        return {
            "type": "text",
            "data": final_data,
            "count": len(final_data)
        }
