from bs4 import BeautifulSoup
import re

def analyze():
    print("Analyzing zolo_detail_dump.html...")
    try:
        with open('zolo_detail_dump.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        print("zolo_detail_dump.html not found.")
        return

    soup = BeautifulSoup(html, 'html.parser')

    # Deep search for Description
    print("\n--- Deep Description Search ---")
    # Search for text content that is long
    for tag in soup.find_all(['div', 'section', 'p']):
        text = tag.get_text(strip=True)
        if len(text) > 100 and "Zolo" not in text[:50] and "Copyright" not in text:
            print(f"Possible Description ({tag.name} class={tag.get('class')}): {text[:100]}...")

    # Deep search for Property Type
    print("\n--- Deep Property Type Search ---")
    type_label = soup.find(string=re.compile("Type|Style"))
    if type_label:
        parent = type_label.find_parent()
        print(f"Found 'Type/Style' label in {parent.name}: {parent.get_text(strip=True)}")
        
    # Amenities check
    print("\n--- Deep Amenities Search ---")
    am_section = soup.find(string=re.compile("Amenities|Features"))
    if am_section:
        parent = am_section.find_parent().find_parent() # Go up a bit
        print(f"Amenities container candidate: {parent.get_text()[:200]}")

if __name__ == "__main__":
    analyze()
