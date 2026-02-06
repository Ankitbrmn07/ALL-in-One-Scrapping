import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.browser import BrowserManager

async def main():
    print("Starting debug script for detail page...")
    async with BrowserManager(headless=True) as bm:
        print("Browser started.")
        page = await bm.get_page()
        url = "https://www.zolo.ca/south-bay-real-estate/159-south-bay-6-madinat-al-mataar-dubai-uae"
        print(f"Navigating to {url}...")
        await page.goto(url, timeout=60000)
        print("Waiting for load...")
        await page.wait_for_timeout(5000) 
        
        content = await page.content()
        with open("zolo_detail_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Dumped zolo_detail_dump.html")

if __name__ == "__main__":
    asyncio.run(main())
