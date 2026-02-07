import json
from bs4 import BeautifulSoup

def test_json_extraction():
    with open("fashion_rendered.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find("script", id="__NEXT_DATA__")
    
    if script:
        data = json.loads(script.string)
        print("Found __NEXT_DATA__ JSON")
        
        # Traverse to find articles
        # Path based on visual inspection: props.pageProps.apolloState
        apollo_state = data.get('props', {}).get('pageProps', {}).get('apolloState', {})
        
        articles = []
        for key, value in apollo_state.items():
            if key.startswith('LocalNewsArticle:'):
                articles.append(value)
                
        print(f"Found {len(articles)} articles in JSON.")
        if articles:
            print("Sample Article:")
            print(json.dumps(articles[0], indent=2))
    else:
        print("Could not find __NEXT_DATA__ script.")

if __name__ == "__main__":
    test_json_extraction()
