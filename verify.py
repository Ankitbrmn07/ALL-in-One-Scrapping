import asyncio
from core.browser import BrowserManager
from agents.classifier import ContentClassifier
from extractors.text import TextExtractor
from config import settings

async def verify():
    settings.HEADLESS = True
    print("STARTING VERIFY...")
    async with BrowserManager() as bm:
        print("BROWSER STARTED")
        page = await bm.get_page()
        print("PAGE GET")
        await page.goto("https://example.com")
        print("NAVIGATED")
        
        classifier = ContentClassifier()
        analysis = await classifier.classify(page)
        print(f"CLASSIFIED: {analysis.content_type}")
        
        extractor = TextExtractor(page)
        result = await extractor.extract()
        print(f"EXTRACTED: {result}")
        
        # Test write
        from pipelines.exporter import Exporter
        Exporter.to_json(result, "verify_result.json")
        print("EXPORTED")

if __name__ == "__main__":
    asyncio.run(verify())
