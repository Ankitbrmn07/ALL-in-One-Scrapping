from typing import Dict, Any, List
from extractors.base import BaseExtractor
from core.types import ContentType
import logging

class ImageExtractor(BaseExtractor):
    def __init__(self, page):
        super().__init__(page)
        self.logger = logging.getLogger("ImageExtractor")

    def supports(self, content_type: ContentType) -> bool:
        return content_type == ContentType.IMAGE_GALLERY

    async def extract(self) -> Dict[str, Any]:
        self.logger.info("Extracting images...")
        
        # 1. Scroll to bottom to trigger lazy loading
        await self._scroll_to_bottom()
        
        # 2. Extract
        # We look for src, data-src, and srcset
        images = await self.page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs.map(img => {
                return {
                    src: img.src,
                    data_src: img.getAttribute('data-src'),
                    alt: img.alt,
                    width: img.width,
                    height: img.height
                }
            }).filter(i => i.src && i.width > 50 && i.height > 50); // Filter small icons
        }""")
        
        self.logger.info(f"Found {len(images)} images.")
        
        # Deduplicate and Clean
        valid_urls = set()
        cleaned_images = []
        for img in images:
            url = img.get("src") or img.get("data_src")
            if url and url not in valid_urls:
                valid_urls.add(url)
                cleaned_images.append({
                    "url": url,
                    "alt": img.get("alt")
                })

        return {
            "type": "images",
            "count": len(cleaned_images),
            "data": cleaned_images
        }

    async def _scroll_to_bottom(self):
        """Helper to scroll page slowly to trigger lazy loads."""
        self.logger.info("Scrolling for lazy loaded images...")
        previous_height = await self.page.evaluate("document.body.scrollHeight")
        while True:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(1000) # Wait for load
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height
