from playwright.async_api import Page
import asyncio
import logging

class CaptchaHandler:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger("CaptchaHandler")

    async def detect_and_solve(self):
        """
        Checks for common CAPTCHA signatures.
        If found, pauses execution for manual solving (Headed) or alerts (Headless).
        """
        
        # Common selectors for captchas (ReCaptcha, hCaptcha, Cloudflare turnstile)
        # Note: Selectors change often. This is a heuristic.
        selectors = [
            "iframe[src*='google.com/recaptcha']",
            "iframe[src*='hcaptcha.com']",
            "iframe[src*='cloudflare']",
            "div.g-recaptcha",
            "#challenge-form", # Cloudflare
        ]
        
        found = False
        for sel in selectors:
            if await self.page.locator(sel).count() > 0:
                self.logger.warning(f"CAPTCHA signature found: {sel}")
                found = True
                break
        
        # Text based check
        if not found:
            text = await self.page.content()
            if "Verify you are human" in text or "Complete the security check" in text:
                self.logger.warning("CAPTCHA text found.")
                found = True

        if found:
            await self.handle_captcha()

    async def handle_captcha(self):
        self.logger.warning("!!! CAPTCHA DETECTED !!!")
        self.logger.warning("Please solve the CAPTCHA in the browser window.")
        self.logger.warning("Execution paused. Press ENTER in the console when solved.")
        
        # Bring browser to front if possible (OS dep, can't strictly enforce from here)
        
        # Simple blocking input for user confirmation
        # In a real async GUI, this would be a callback.
        # For CLI, we use a loop or input (but input blocks async event loop).
        
        # If we are headless, we can't solve it.
        # But our settings default to Headless=True.
        # Ideally, we should detect if we are headless and error out or tell user to restart in headed mode.
        
        from config import settings
        if settings.HEADLESS:
            self.logger.error("CAPTCHA detected in Headless mode. Cannot wait for user input.")
            self.logger.error("Please run with --headed to solve it.")
            # We can either raise exception or return (and likely fail extraction)
            return

        print("\n" + "="*40)
        print(" ACTION REQUIRED: CAPTCHA DETECTED ")
        print(" Solve it in the browser, then press ENTER safely here.")
        print("="*40 + "\n")
        
        await asyncio.get_event_loop().run_in_executor(None, input, "Press Enter after solving...")
        self.logger.info("Resuming execution...")
