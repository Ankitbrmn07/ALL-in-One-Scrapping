import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from config import settings
import logging

class BrowserManager:
    def __init__(self, headless: bool = settings.HEADLESS):
        self.headless = headless
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.logger = logging.getLogger("BrowserManager")

    async def start(self):
        """Starts Playwright and the Browser."""
        self.logger.info(f"Starting browser (Headless: {self.headless})...")
        self.playwright = await async_playwright().start()
        
        # Launch options - can add more args for stealth if needed
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars"
        ]

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=launch_args,
            slow_mo=50 if not self.headless else 0
        )
        
        # Context initialization with storage state if exists
        await self.init_context()
        self.logger.info("Browser started successfully.")

    async def init_context(self):
        """Initializes the browser context with persistance support."""
        context_options = {
            "viewport": settings.VIEWPORT,
            "user_agent": settings.USER_AGENT,
            "accept_downloads": True,
        }

        if settings.STORAGE_STATE_FILE.exists():
            self.logger.info(f"Loading session from {settings.STORAGE_STATE_FILE}")
            context_options["storage_state"] = str(settings.STORAGE_STATE_FILE)

        self.context = await self.browser.new_context(**context_options)
        
        # Add init scripts for stealth
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def get_page(self) -> Page:
        """New page in default context."""
        if not self.context:
            await self.init_context()
        return await self.context.new_page()

    async def close(self):
        """Closes browser and playwright."""
        if self.context:
            # Save state before closing
            await self.context.storage_state(path=str(settings.STORAGE_STATE_FILE))
            self.logger.info(f"Session saved to {settings.STORAGE_STATE_FILE}")
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        self.logger.info("Browser stopped.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
