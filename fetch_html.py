import requests
import sys

def fetch_html(url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Successfully saved {url} to {output_file}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fetch_html.py <url> <output_file>")
    else:
        fetch_html(sys.argv[1], sys.argv[2])
