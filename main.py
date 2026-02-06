import asyncio
import sys
import argparse
import logging
from termcolor import colored

# Setup Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Main")

from core.browser import BrowserManager
from agents.classifier import ContentClassifier
from agents.captcha import CaptchaHandler
from core.types import ContentType
from extractors.media import MediaExtractor
from extractors.images import ImageExtractor
from extractors.text import TextExtractor
from pipelines.downloader import Downloader
from pipelines.exporter import Exporter
from config import settings

from core.router import URLRouter
from extractors.direct_media import DirectMediaHandler
from extractors.zolo import ZoloExtractor

async def run(url: str, headless: bool):
    # Override settings if needed
    settings.HEADLESS = headless
    
    logger.info(colored(f"Starting Scraper for: {url}", "green"))
    
    # 0. Check Route
    strategy = URLRouter.get_route_strategy(url)
    logger.info(f"Selected Strategy: {strategy}")
    
    if strategy == "DIRECT_MEDIA":
        # Fast path, no browser overhead
        handler = DirectMediaHandler()
        # Note: extract is synchronous in our simple wrapper, but we wrap it 
        result = await asyncio.get_event_loop().run_in_executor(None, handler.extract, url)
        
        if not result.get("error"):
            logger.info(colored("Direct Extraction Successful!", "green"))
             # Download Logic
            # For direct yt-dlp, usually we want to let yt-dlp download it fully if user wants.
            # But here we just show info or download thumbnail
             
            Exporter.to_json(result, "extraction_summary.json")
            return
        else:
             logger.warning("Direct extraction failed, falling back to Browser...")
             # Fallthrough to browser

    async with BrowserManager(headless=headless) as bm:
        page = await bm.get_page()
        
        try:
            logger.info("Navigating...")
            await page.goto(url, wait_until="domcontentloaded", timeout=settings.BROWSER_TIMEOUT)
            
            # 1. CAPTCHA Check
            captcha = CaptchaHandler(page)
            await captcha.detect_and_solve()
            
            # 2. Analyze/Classify
            classifier = ContentClassifier()
            analysis = await classifier.classify(page)
            
            logger.info(colored(f"Detected Type: {analysis.content_type.value}", "cyan"))
            
            # 3. Select Strategy
            # 3. Select Strategy
            scanner = None
            if "zolo.ca" in url:
                scanner = ZoloExtractor(page)
            elif analysis.content_type in [ContentType.VIDEO_PLATFORM, ContentType.VIDEO_EMBED]:
                scanner = MediaExtractor(page)
            elif analysis.content_type == ContentType.IMAGE_GALLERY:
                scanner = ImageExtractor(page)
            elif analysis.content_type == ContentType.ARTICLE:
                scanner = TextExtractor(page)
            else:
                 # Default to Text for now, or fallback
                logger.warning("Generic/Unknown type, defaulting to text extraction.")
                scanner = TextExtractor(page)

            # 4. Extract
            result = await scanner.extract()
            logger.info(colored("Extraction Complete!", "green"))
            
            # 5. Pipeline / Download
            downloader = Downloader()
            
            if result.get("type") == "media":
                d_url = result.get("download_url")
                
                # Check if extractor supports direct download capability
                if hasattr(scanner, 'download'):
                    logger.info("Initiating download via Extractor (using session cookies)...")
                    await scanner.download()
                    logger.info(colored("Download Complete!", "green"))
                    
                elif d_url:
                    logger.info("Found media stream/file, downloading...")
                    if result.get("strategy") == "direct" or "youtube" in result.get("url", ""):
                         logger.info("Video is hosted on platform. Use yt-dlp CLI to download best quality.")
                    else:
                         await downloader.download_file(d_url, folder="video")
                         
            elif result.get("type") == "images":
                images = result.get("data", [])
                logger.info(f"Downloading {len(images)} images...")
                urls = [img['url'] for img in images]
                await downloader.download_batch(urls, folder="images")
                
            elif result.get("type") == "text":
                logger.info("Saving text content...")
                data = result["data"]
                Exporter.to_json(data, "article.json")
                
                # Export to CSV if data is a list (typical for scrapers like Zolo)
                if isinstance(data, list) and len(data) > 0:
                    logger.info("Exporting to CSV...")
                    Exporter.to_csv(data, "zolo_results.csv")
                
            # Save metadata
            Exporter.to_json(result, "extraction_summary.json")
            
        except Exception as e:
            logger.error(colored(f"Critical Error: {e}", "red"))
            import traceback
            traceback.print_exc()

        # Pause to see result if headed
        if not headless:
            await asyncio.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Universal Web Scraper")
    parser.add_argument("url", help="Target Website URL")
    parser.add_argument("--headed", action="store_true", help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    asyncio.run(run(args.url, not args.headed))

if __name__ == "__main__":
    main()
