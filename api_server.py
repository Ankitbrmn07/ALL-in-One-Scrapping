from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from datetime import datetime

# Import scraper components
from scraper.core.browser_manager import BrowserManager
from scraper.core.exporter import Exporter
from scraper.categories.biography.wikipedia import WikipediaScraper
from scraper.categories.politics.bbc import BBCScraper
from scraper.categories.health.healthline import HealthlineScraper
from scraper.categories.bollywood.filmibeat import FilmiBeatScraper
# New Imports
from scraper.categories.bollywood.bollywoodhungama import BollywoodHungamaScraper
from scraper.categories.bollywood.imdb import IMDbScraper
from scraper.categories.health.who import WHOScraper
from scraper.categories.health.nih import NIHScraper
from scraper.categories.fitness.healthline_fitness import HealthlineFitnessScraper
from scraper.categories.fitness.menshealth import MensHealthScraper
from scraper.categories.technology.gadgets360 import Gadgets360Scraper
from scraper.categories.sports.espncricinfo import ESPNCricinfoScraper
from scraper.categories.sports.sportskeeda import SportskeedaScraper
from scraper.categories.travel.lonelyplanet import LonelyPlanetScraper
from scraper.categories.fashion.fashionunited import FashionUnitedScraper
from scraper.categories.business.business_insider import BusinessInsiderScraper
from scraper.categories.entertainment.people import PeopleScraper
from scraper.categories.real_estate import DubizzleScraper, BayutScraper, PropertyFinderScraper, EmaarScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Scraper Class Mapping
SCRAPER_CLASSES = {
    "wikipedia": WikipediaScraper,
    "bbc": BBCScraper,
    "healthline": HealthlineScraper,
    "filmibeat": FilmiBeatScraper,
    "bollywoodhungama": BollywoodHungamaScraper,
    "imdb": IMDbScraper,
    "who": WHOScraper,
    "nih": NIHScraper,
    "healthline_fitness": HealthlineFitnessScraper,
    "menshealth": MensHealthScraper,
    "gadgets360": Gadgets360Scraper,
    "espncricinfo": ESPNCricinfoScraper,
    "sportskeeda": SportskeedaScraper,
    "lonelyplanet": LonelyPlanetScraper,
    "fashionunited": FashionUnitedScraper,
    "business_insider": BusinessInsiderScraper,
    "people": PeopleScraper,
    "dubizzle": DubizzleScraper,
    "bayut": BayutScraper,
    "property_finder": PropertyFinderScraper,
    "emaar": EmaarScraper
}

# Category to Website Mapping
CATEGORY_WEBSITES = {
    "biography": [
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Main_Page", "scraper": "wikipedia"}
    ],
    "bollywood": [
        {"name": "FilmiBeat", "url": "https://www.filmibeat.com/", "scraper": "filmibeat"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/", "scraper": "bollywoodhungama"},
        {"name": "IMDb", "url": "https://www.imdb.com/", "scraper": "imdb"}
    ],
    "politics": [
        {"name": "BBC", "url": "https://www.bbc.com/", "scraper": "bbc"}
    ],
    "health": [
        {"name": "WHO", "url": "https://www.who.int/", "scraper": "who"},
        {"name": "NIH", "url": "https://www.nih.gov/", "scraper": "nih"},
        {"name": "Healthline", "url": "https://www.healthline.com/", "scraper": "healthline"}
    ],
    "fitness": [
        {"name": "Healthline Fitness", "url": "https://www.healthline.com/fitness", "scraper": "healthline_fitness"},
        {"name": "Men's Health", "url": "https://www.menshealth.com/", "scraper": "menshealth"}
    ],
    "technology": [
        {"name": "Gadgets 360", "url": "https://www.gadgets360.com/", "scraper": "gadgets360"}
    ],
    "sports": [
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com/", "scraper": "espncricinfo"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com/", "scraper": "sportskeeda"}
    ],
    "travel": [
        {"name": "Lonely Planet", "url": "https://www.lonelyplanet.com/", "scraper": "lonelyplanet"}
    ],
    "fashion": [
        {"name": "Fashion United", "url": "https://fashionunited.in/news/fashion", "scraper": "fashionunited"}
    ],
    "business": [
        {"name": "Business Insider", "url": "https://www.businessinsider.com/", "scraper": "business_insider"}
    ],
    "entertainment": [
        {"name": "People", "url": "https://people.com/", "scraper": "people"}
    ],
    "real_estate": [
        {"name": "Dubizzle UAE", "url": "https://dubai.dubizzle.com/en/property-for-sale/residential/", "scraper": "dubizzle"},
        {"name": "Bayut", "url": "https://www.bayut.com/for-sale/property/uae/", "scraper": "bayut"},
        {"name": "Property Finder UAE", "url": "https://www.propertyfinder.ae/en/search?c=2&fu=0&rp=y&ob=mr", "scraper": "property_finder"},
        {"name": "Emaar Properties", "url": "https://properties.emaar.com/en/our-communities/", "scraper": "emaar"}
    ]
}

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    Returns all available categories
    """
    categories = list(CATEGORY_WEBSITES.keys())
    return jsonify({
        "success": True,
        "categories": categories
    })

@app.route('/api/websites/<category>', methods=['GET'])
def get_websites_by_category(category):
    """
    Returns websites for a specific category
    """
    if category not in CATEGORY_WEBSITES:
        return jsonify({
            "success": False,
            "error": "Invalid category"
        }), 400
    
    websites = CATEGORY_WEBSITES[category]
    return jsonify({
        "success": True,
        "category": category,
        "websites": websites
    })

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """
    Main scraping endpoint
    Expected JSON payload:
    {
        "category": "biography",
        "websites": ["wikipedia"],
        "dataTypes": ["text", "images"],
        "outputFormat": "csv"
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        category = data.get('category')
        websites = data.get('websites', [])
        data_types = data.get('dataTypes', ['text'])
        output_format = data.get('outputFormat', 'csv')
        
        if not category:
            return jsonify({"success": False, "error": "Category is required"}), 400
        
        if not websites:
            return jsonify({"success": False, "error": "At least one website must be selected"}), 400
        
        logger.info(f"Scraping request: category={category}, websites={websites}")
        
        # Run scraping in async context
        results = asyncio.run(run_scraping(category, websites, data_types, output_format))
        
        return jsonify({
            "success": True,
            "category": category,
            "websites": websites,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

async def run_scraping(category, websites, data_types, output_format):
    """
    Run the actual scraping logic
    """
    all_results = []
    
    async with BrowserManager(headless=False) as bm:
        page = await bm.get_page()
        
        for website_key in websites:
            try:
                # Map website to scraper class
                scraper_class = SCRAPER_CLASSES.get(website_key)
                
                if not scraper_class:
                    logger.warning(f"No scraper implementation for: {website_key}")
                    continue
                
                # Instantiate scraper
                scraper = scraper_class(page)
                
                # Run scraper
                logger.info(f"Starting scraper for: {website_key}")
                data = await scraper.scrape()
                
                logger.info(f"DEBUG: Scraper returned {len(data)} items")
                
                # Save data to disk
                import os
                
                output_dir = f"data/{category}"
                logger.info(f"DEBUG: Creating directory: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
                
                file_path_csv = f"{output_dir}/{website_key}_data.csv"
                file_path_json = f"{output_dir}/{website_key}_data.json"
                
                if output_format == 'csv':
                    Exporter.to_csv(data, file_path_csv)
                    logger.info(f"Saved CSV to: {os.path.abspath(file_path_csv)}")
                elif output_format == 'json':
                    Exporter.to_json(data, file_path_json)
                    logger.info(f"Saved JSON to: {os.path.abspath(file_path_json)}")
                else:
                    # Save both by default context or specific requirement
                    Exporter.to_csv(data, file_path_csv)
                    Exporter.to_json(data, file_path_json)
                    logger.info(f"Saved data to: {os.path.abspath(output_dir)}")

                all_results.append({
                    "website": website_key,
                    "items_scraped": len(data),
                    "saved_at": os.path.abspath(output_dir),
                    "data": data[:10]  # Return first 10 items for preview
                })
                
            except Exception as e:
                logger.error(f"Error scraping {website_key}: {str(e)}")
                all_results.append({
                    "website": website_key,
                    "error": str(e)
                })
    
    return all_results

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Flask API Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
