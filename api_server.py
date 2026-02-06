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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Category to Website Mapping
CATEGORY_WEBSITES = {
    "biography": [
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Main_Page", "scraper": "wikipedia"}
    ],
    "bollywood": [
        {"name": "FilmiBeat", "url": "https://www.filmibeat.com/", "scraper": None},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/", "scraper": None},
        {"name": "IMDb", "url": "https://www.imdb.com/", "scraper": None}
    ],
    "politics": [
        {"name": "BBC", "url": "https://www.bbc.com/", "scraper": "bbc"}
    ],
    "health": [
        {"name": "WHO", "url": "https://www.who.int/", "scraper": None},
        {"name": "NIH", "url": "https://www.nih.gov/", "scraper": None},
        {"name": "Healthline", "url": "https://www.healthline.com/", "scraper": "healthline"}
    ],
    "fitness": [
        {"name": "Healthline Fitness", "url": "https://www.healthline.com/fitness", "scraper": None},
        {"name": "Men's Health", "url": "https://www.menshealth.com/", "scraper": None}
    ],
    "technology": [
        {"name": "Gadgets 360", "url": "https://www.gadgets360.com/", "scraper": None}
    ],
    "sports": [
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com/", "scraper": None},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com/", "scraper": None}
    ],
    "travel": [
        {"name": "Lonely Planet", "url": "https://www.lonelyplanet.com/", "scraper": None}
    ],
    "fashion": [
        {"name": "Fashion United", "url": "http://fashionunited.in/", "scraper": None}
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
    
    async with BrowserManager(headless=True) as bm:
        page = await bm.get_page()
        
        for website_scraper in websites:
            try:
                # Map website to scraper class
                scraper = None
                
                if website_scraper == "wikipedia":
                    scraper = WikipediaScraper(page)
                elif website_scraper == "bbc":
                    scraper = BBCScraper(page)
                elif website_scraper == "healthline":
                    scraper = HealthlineScraper(page)
                elif website_scraper == "filmibeat":
                    scraper = FilmiBeatScraper(page)
                else:
                    logger.warning(f"No scraper implementation for: {website_scraper}")
                    continue
                
                # Run scraper
                logger.info(f"Starting scraper for: {website_scraper}")
                data = await scraper.scrape()
                
                logger.info(f"DEBUG: Scraper returned {len(data)} items")
                
                # Save data to disk
                import os
                
                output_dir = f"data/{category}"
                logger.info(f"DEBUG: Creating directory: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"DEBUG: Directory created or exists")
                
                file_path_csv = f"{output_dir}/{website_scraper}_data.csv"
                file_path_json = f"{output_dir}/{website_scraper}_data.json"
                
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
                    "website": website_scraper,
                    "items_scraped": len(data),
                    "saved_at": os.path.abspath(output_dir),
                    "data": data[:10]  # Return first 10 items for preview
                })
                
            except Exception as e:
                logger.error(f"Error scraping {website_scraper}: {str(e)}")
                all_results.append({
                    "website": website_scraper,
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
