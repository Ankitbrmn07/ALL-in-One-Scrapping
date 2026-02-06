
import os
import re

def save_matches():
    path = r"d:\Project\clone\SCRAPPING\ALL-in-One-Scrapping\imdb_rendered.html"
    output_path = r"d:\Project\clone\SCRAPPING\ALL-in-One-Scrapping\imdb_matches.txt"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    keyword = "3 Idiots"
    matches = [m.start() for m in re.finditer(re.escape(keyword), content)]
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"Found {len(matches)} occurrences of '{keyword}'.\n\n")
        
        for i, index in enumerate(matches):
            start = max(0, index - 500)
            end = min(len(content), index + 500)
            snippet = content[start:end] # Keep newlines
            out.write(f"--- Match {i+1} at index {index} ---\n")
            out.write(snippet)
            out.write("\n\n")

    print(f"Saved matches to {output_path}")

if __name__ == "__main__":
    save_matches()
