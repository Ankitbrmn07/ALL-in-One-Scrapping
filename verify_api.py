import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_health():
    print(f"Testing Health Endpoint: http://localhost:5000/health")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")

def test_categories():
    print(f"\nTesting Categories Endpoint: {BASE_URL}/categories")
    try:
        response = requests.get(f"{BASE_URL}/categories")
        print(f"Categories: {response.json().get('categories')}")
    except Exception as e:
        print(f"Categories check failed: {e}")

def test_scrape_filmibeat():
    print("\nTesting Scrape Endpoint (FilmiBeat)...")
    payload = {
        "category": "bollywood",
        "websites": ["filmibeat"],
        "dataTypes": ["text"],
        "outputFormat": "json"
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/scrape", json=payload, timeout=60)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get("success"):
            print("✅ Scraping Successful!")
            results = data.get("results", [])
            for res in results:
                print(f"Website: {res.get('website')}")
                print(f"Items Scraped: {res.get('items_scraped')}")
                # Print first item title if available
                if res.get("data") and len(res.get("data")) > 0:
                    print(f"First Item: {res.get('data')[0].get('title')}")
        else:
            print(f"❌ Scraping Failed: {data.get('error')}")
            
        print(f"Time Taken: {end_time - start_time:.2f}s")
        
    except Exception as e:
        print(f"Scrape request failed: {e}")

if __name__ == "__main__":
    print("Starting API Verification...")
    test_health()
    test_categories()
    test_scrape_filmibeat()
