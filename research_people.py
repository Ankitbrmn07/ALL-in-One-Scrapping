import requests
from bs4 import BeautifulSoup
import json

def fetch_people():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        url = "https://people.com/"
        response = requests.get(url, headers=headers, timeout=20)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find potential article links
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                if len(text) > 20 and 'people.com' in href or href.startswith('/'):
                    links.append({'text': text, 'href': href})
            
            print("\nPotential Article Links (first 10):")
            for l in links[:10]:
                print(f"- {l['text']}: {l['href']}")
                
            # Find potential pagination
            next_page = soup.find('a', {'rel': 'next'})
            print(f"\nNext Page link: {next_page['href'] if next_page else 'None'}")
            
            # Also look for common People.com article selectors
            # People.com often uses .card or .mntl-card-list-items
            cards = soup.select('.card, .mntl-card-list-items, article')
            print(f"\nFound {len(cards)} card/article elements.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_people()
