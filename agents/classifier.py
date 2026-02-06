from playwright.async_api import Page
from core.types import ContentType, PageAnalysis
import logging

class ContentClassifier:
    def __init__(self):
        self.logger = logging.getLogger("ContentClassifier")

    async def classify(self, page: Page) -> PageAnalysis:
        """Analyzes the page DOM to determine its primary content type."""
        
        # 1. Basic Metadata
        title = await page.title()
        try:
            description = await page.locator("meta[name='description']").get_attribute("content")
        except:
            description = ""

        # 2. Heuristic Scoring
        scores = {ctype: 0.0 for ctype in ContentType}
        
        # -- Check Video --
        video_tags = await page.locator("video").count()
        iframes = await page.locator("iframe").count()
        # Basic check for known video platforms in URL
        url = page.url
        if "youtube.com" in url or "vimeo.com" in url or "dailymotion.com" in url:
            scores[ContentType.VIDEO_PLATFORM] += 10.0
        
        if video_tags > 0:
            scores[ContentType.VIDEO_EMBED] += (video_tags * 2.0)
        
        # -- Check Images --
        img_tags = await page.locator("img").count()
        if img_tags > 10:
            # Check if they are substantial images, not just icons (harder without analyzing sizes, but simplified for now)
            scores[ContentType.IMAGE_GALLERY] += (img_tags * 0.2)

        # -- Check Article / Text --
        # Look for <article>, or high p-tag count
        is_article_tag = await page.locator("article").count()
        p_tags = await page.locator("p").count()
        
        if is_article_tag > 0:
            scores[ContentType.ARTICLE] += 5.0
        if p_tags > 20: 
            scores[ContentType.ARTICLE] += (p_tags * 0.1)

        # -- Check Product --
        # Look for price patterns or schema.org Product
        # This is a basic check.
        try:
            schema_type = await page.evaluate("() => document.querySelector('script[type=\"application/ld+json\"]')?.innerText")
            if schema_type and "Product" in schema_type:
                scores[ContentType.PRODUCT] += 10.0
        except:
            pass
            
        # Determine Winner
        # Filter out unknown if scores are too low? For now just max.
        best_match = max(scores, key=scores.get)
        
        # Special case: Youtube is always video platform
        if "youtube.com" in url: 
            best_match = ContentType.VIDEO_PLATFORM

        self.logger.info(f"Page classified as: {best_match.value} (Scores: {scores})")
        
        return PageAnalysis(
            content_type=best_match,
            title=title,
            description=description or "",
            score_details=scores
        )
