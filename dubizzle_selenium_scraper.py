import os
import sys
import time
import random
import re
import csv
import hashlib
import json
import logging
from datetime import datetime
# import undetected_chromedriver as uc # Disabled due to WinError 6
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# ==============================================================================
# CONFIGURATION & LOGGING
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("dubizzle_scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# HELPERS
# ==============================================================================

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# To use a proxy, format: "ip:port" or "user:pass@ip:port"
# Example: PROXY = "123.45.67.89:8080"
PROXY = None 

def cleanup_chrome():
    """Force kill stuck chrome processes to free up the profile folder."""
    try:
        if os.name == 'nt':
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
    except:
        pass

def setup_driver():
    """
    Initialize Chrome driver with anti-detection, persistent profile, and optional proxy.
    """
    cleanup_chrome() # Ensure no locks on profile
    
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    
    # Proxy Support
    if PROXY:
        options.add_argument(f'--proxy-server={PROXY}')
        
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service() 
    
    # Use a persistent profile to save cookies/CAPTCHA tokens
    profile_dir = os.path.join(os.getcwd(), "selenium_profile")
    options.add_argument(f"user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # Anti-bot scripts
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def smart_scroll(driver, max_scrolls=20):
    """
    Scrolls down to load more items.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
             # Try to find a "Next" button if scrolling stops working
             try:
                 next_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Next') or contains(text(), '>')]")
                 if next_btns:
                     next_btns[0].click()
                     time.sleep(4)
                     continue
             except:
                 pass
             
             logger.info("End of page reached.")
             break
        last_height = new_height
        logger.info(f"Scrolled {i+1}/{max_scrolls}")

def safe_extract(element, xpath, default="N/A", attr=None):
    try:
        target = element.find_element(By.XPATH, xpath)
        if attr:
            return target.get_attribute(attr)
        return target.text.strip()
    except:
        return default

def clean_text(text):
    if not text: return "N/A"
    return re.sub(r'\s+', ' ', text).strip()

def get_currency_price(text):
    # e.g. "AED 120,000" -> "AED", 120000.0
    if not text: return "AED", 0.0
    
    # Extract numbers
    clean_val = re.sub(r'[^\d.]', '', text)
    try:
        price = float(clean_val)
    except:
        price = 0.0
        
    # Extract currency (simple regex)
    curr_match = re.search(r'([A-Z]{3})', text)
    currency = curr_match.group(1) if curr_match else "AED"
    
    return currency, price

# ==============================================================================
# EXTRACTION LOGIC
# ==============================================================================

def extract_listings(driver, writer):
    # Heuristic: Listing cards usually have a specific data-testid or class.
    # We'll try to find them by looking for the "AED" text which is common in price 
    # and then finding the parent container.
    
    logger.info("Analyzing page structure...")
    
    # Wait for atleast one price element
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'AED')]"))
        )
    except:
        logger.error("Timeout waiting for content.")
        return

    # Finding all potential listing cards
    # Strategy: Find all article or div elements that contain price information
    # Dubizzle 2024 often uses <article> tags or divs with data-testid="listing-card"
    
    cards = []
    
    # Try strategy 1: data-testid
    cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='listing-card'], [data-testid='property-card']")
    
    # Try strategy 2: Generic classes if 1 fails
    if not cards:
        cards = driver.find_elements(By.CSS_SELECTOR, "div[class*='ListItem'], article")
        
    logger.info(f"Found {len(cards)} potential listings.")
    
    for i, card in enumerate(cards):
        try:
            # 1. Source URL
            source_url = "N/A"
            try:
                # Usually the card is a link or contains a link
                link_el = card.find_element(By.TAG_NAME, "a")
                source_url = link_el.get_attribute("href")
            except: 
                source_url = driver.current_url

            # 2. Price & Currency
            # Look for element with digits and 'AED'
            raw_price = safe_extract(card, ".//*[contains(text(), 'AED')]", "N/A")
            currency, price = get_currency_price(raw_price)
            
            # 3. Title / Description
            # Usually H2 or H3
            title = "N/A"
            for tag in ["h2", "h3", "h1"]:
                try:
                    t_el = card.find_element(By.TAG_NAME, tag)
                    if t_el.text.strip():
                        title = t_el.text.strip()
                        break
                except: continue
                
            # 4. Address / City / Location
            # Often secondary text. heuristic: contains "Dubai" or "Street" or is after the title
            # Let's try to get all text and parse.
            all_text = card.text.split('\n')
            address = "N/A"
            # Simple heuristic: The longest line that isn't the title or price usually address or description
            # Or look for specific location icon class? Hard without visual inspector.
            # Fallback: Just grab the text that looks like a location (e.g. at the bottom)
            if len(all_text) > 3:
                 # Usually: Price, Title, Address, Beds/Baths
                 address = all_text[-2] # simplified guess
            else:
                 address = safe_extract(card, ".//*[@data-testid='sub-heading']", "N/A")

            # 5. Type (Residential/Commercial)
            # URL context suggests Residential
            property_type = "Residential"
            
            # 6. Images
            images = []
            try:
                imgs = card.find_elements(By.TAG_NAME, "img")
                for img in imgs:
                    src = img.get_attribute("src")
                    if src and "http" in src:
                        images.append(src)
            except: pass
            image_str = images[0] if images else "N/A"
            
            # 7. Amenities (Beds/Baths/Area)
            # Search for numbers followed by "Bed", "Bath", "sqft"
            card_text = card.text
            amenities = []
            
            beds_match = re.search(r'(\d+)\s*Bed', card_text, re.IGNORECASE)
            if beds_match: amenities.append(f"{beds_match.group(1)} Beds")
            
            baths_match = re.search(r'(\d+)\s*Bath', card_text, re.IGNORECASE)
            if baths_match: amenities.append(f"{baths_match.group(1)} Baths")
            
            sqft_match = re.search(r'([\d,]+)\s*Sqft', card_text, re.IGNORECASE)
            if sqft_match: amenities.append(f"{sqft_match.group(1)} Sqft")
            
            amenities_str = ", ".join(amenities)

            # 8. Description Raw
            description_raw = f"{title} - {address} - {amenities_str}"

            # WRITE ROW
            # Headers: property_type,description_raw,extra,amenities,price,address,title,currency,city,images,source_url
            writer.writerow([
                property_type,
                description_raw,
                "{}", # extra
                amenities_str,
                price,
                address,
                title,
                currency,
                "Dubai", # City (inferred from URL)
                image_str,
                source_url
            ])
            
            if (i+1) % 5 == 0:
                logger.info(f"Processed {i+1} Listings...")
                
        except Exception as e:
            logger.warning(f"Failed to parse card {i}: {e}")

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    logger.info("Starting Dubizzle Scraper...")
    driver = setup_driver()
    output_file = 'dubizzle_results.csv'
    
    try:
        url = "https://dubai.dubizzle.com/property-for-rent/residential/"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Give manual time for CAPTCHA - CRITICAL FOR INCAPSULA
        print("\n" + "!"*80)
        print("PLEASE SOLVE ANY CAPTCHA/BLOCKING SCREEN IN THE BROWSER NOW.")
        print("Once the property listings are visible, type 'DONE' in the chat.")
        print("IMPORTANT: DO NOT CLOSE THE BROWSER WINDOW!")
        print("The script needs the browser to remain open to scrape the data.")
        print("Waiting for signal file 'start.signal'...")
        print("!"*80 + "\n")
        
        # File-based signal wait loop
        while not os.path.exists("start.signal"):
            time.sleep(1)
            
        logger.info("Signal received! Proceeding with extraction...")
        
        # DEBUG: Save page source to see what we actually loaded
        with open("dubizzle_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("Saved dubizzle_debug.html for inspection.")
        
        # Scroll to load items
        smart_scroll(driver, max_scrolls=10)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # User Requested Headers:
            # property_type,description_raw,extra,amenities,price,address,title,currency,city,images,source_url
            writer.writerow(['property_type','description_raw','extra','amenities','price','address','title','currency','city','images','source_url'])
            
            extract_listings(driver, writer)
            
        logger.info(f"Done. Results saved to {output_file}")
        
    except Exception as e:
        logger.critical(f"Scraper crashed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
