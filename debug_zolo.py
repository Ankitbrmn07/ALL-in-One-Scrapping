import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.browser import BrowserManager

async def main():
    print("Starting debug script...")
    async with BrowserManager(headless=True) as bm:
        print("Browser started.")
        page = await bm.get_page()
        print("Navigating to Zolo...")
        await page.goto("https://www.zolo.ca/map-search?sarea=Dubai&s_r=1&filter=1", timeout=60000)
        print("Waiting for load...")
        await page.wait_for_timeout(10000) # Wait 10s
        
        content = await page.content()
        with open("zolo_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Dumped zolo_dump.html")

if __name__ == "__main__":
    asyncio.run(main())
