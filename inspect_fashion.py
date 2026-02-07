import asyncio
from playwright.async_api import async_playwright
import os

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://fashionunited.in/news/fashion"
        print(f"Navigating to {url}...")
        await page.goto(url, timeout=60000)
        
        # Wait for content to load
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass
            
        content = await page.content()
        
        with open("fashion_rendered.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("HTML content saved to fashion_rendered.html")
        
        # Try to locate potential items
        articles = await page.locator("article").all()
        print(f"Found {len(articles)} 'article' tags.")
        
        links = await page.locator("a h2").all()
        print(f"Found {len(links)} links with h2.")
        
        # Check specific classes
        mui_grids = await page.locator(".MuiGrid-item").all()
        print(f"Found {len(mui_grids)} .MuiGrid-item elements.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
