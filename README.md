# Web Scraping System - Quick Start Guide

## 🚀 How to Run the System

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 2. Start the Flask API Server
```bash
python api_server.py
```
The server will start on `http://localhost:5000`

### 3. Open the Web Interface
- Open `scraper_ui.html` in your web browser
- Or use a local server:
```bash
python -m http.server 8080
```
Then visit: `http://localhost:8080/scraper_ui.html`

## 📋 How to Use

### Step 1: Select Category
Choose from categories like Biography, Politics, Health, etc.

### Step 2: Select Websites
Once you select a category, available websites will appear automatically.
Select one or more websites to scrape.

### Step 3: Choose Data Types
Select what type of data to extract (Text, Images, Videos, etc.)

### Step 4: Select Output Format
Choose CSV or JSON format for the results.

### Step 5: Start Scraping
Click "Start Scraping" and watch the progress!

## 🎯 Available Scrapers

Currently implemented:
- ✅ **Wikipedia** (Biography) - Working
- ✅ **BBC** (Politics) - Working
- ✅ **Healthline** (Health) - Working

Coming soon (need implementation):
- 🔄 FilmiBeat, Bollywood Hungama, IMDb (Bollywood)
- 🔄 WHO, NIH (Health)
- 🔄 Healthline Fitness, Men's Health (Fitness)
- 🔄 Gadgets 360 (Technology)
- 🔄 ESPN Cricinfo, Sportskeeda (Sports)
- 🔄 Lonely Planet (Travel)
- 🔄 Fashion United (Fashion)

## 🔗 API Endpoints

- `GET /health` - Check server status
- `GET /api/categories` - Get all available categories
- `GET /api/websites/<category>` - Get websites for a category
- `POST /api/scrape` - Start scraping (see api_server.py for payload format)

## 📂 Output Location

Scraped data is saved in:
- `data/<category>/<website>_data.csv`
- `data/<category>/<website>_data.json`

## 🛠️ Troubleshooting

**Problem**: "Failed to connect to backend"
- **Solution**: Make sure Flask server is running: `python api_server.py`

**Problem**: No websites appear after selecting category
- **Solution**: Check browser console (F12) for JavaScript errors

**Problem**: CORS errors
- **Solution**: Flask-CORS should handle this, but ensure it's installed: `pip install flask-cors`
