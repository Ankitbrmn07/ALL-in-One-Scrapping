
import asyncio
from scraper.core.browser_manager import BrowserManager

async def main():
    print("Starting Debug V2 for Dubizzle...")
    # Force headless=False to potentially bypass simple headless checks
    async with BrowserManager(headless=False) as bm:
        page = await bm.get_page()
        
        print("Navigating to Dubizzle...")
        await page.goto("https://dubai.dubizzle.com/en/property-for-sale/residential/", wait_until="domcontentloaded")
        
        print("Waiting 15 seconds for potential redirects/challenges...")
        await page.wait_for_timeout(15000)
        
        title = await page.title()
        print(f"Current Page Title: {title}")
        
        # Check for common block text
        content = await page.content()
        if "Incapsula" in content or "security" in title.lower():
            print("BLOCK DETECTED: Incapsula/Security challenge found.")
        else:
            print("Page seems loaded (or different block).")
            
        # Try to find the listing selector
        try:
             count = await page.locator("[data-testid='listing-card'], article").count()
             print(f"Found {count} listing items with current selector.")
        except Exception as e:
             print(f"Error checking selector: {e}")

        with open("dubizzle_debug_v2.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Dumped HTML to dubizzle_debug_v2.html")

if __name__ == "__main__":
    asyncio.run(main())
