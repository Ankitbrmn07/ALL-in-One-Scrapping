
import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    """
    Initialize Chrome driver with anti-detection and performance settings.
    """
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service() 
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def main():
    driver = setup_driver()
    try:
        url = "https://dubai.dubizzle.com/property-for-rent/residential/"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        print("\n" + "="*60)
        print("ACTION REQUIRED: Check the opened browser window.")
        print("1. If you see a CAPTCHA or blocking screen, please solve it.")
        print("2. Navigate or wait until the property listings are clearly visible.")
        print("3. Return here and press ENTER to save the page structure.")
        print("="*60 + "\n")
        
        input("Press Enter to continue...")
        
        # Save page source
        filename = "dubizzle_source.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        logger.info(f"Successfully saved '{filename}'. You can now close the browser.")
        print(f"File saved: {filename}")
        
    except Exception as e:
        logger.error(f"Error fetching page: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
