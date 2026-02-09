
import asyncio
from scraper.core.browser_manager import BrowserManager

SITES = {
    "Bayut": "https://www.bayut.com/for-sale/property/uae/",
    "PropertyFinder": "https://www.propertyfinder.ae/en/search?c=2&fu=0&rp=y&ob=mr",
    "Emaar": "https://properties.emaar.com/en/our-communities/"
}

async def main():
    async with BrowserManager(headless=False) as bm:
        page = await bm.get_page()
        
        for name, url in SITES.items():
            print(f"Navigating to {name}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(10000) # Wait for renders
                
                content = await page.content()
                with open(f"debug_{name.lower()}.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Saved debug_{name.lower()}.html")
                
            except Exception as e:
                print(f"Error dumping {name}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
