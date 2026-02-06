import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from config import settings

class Exporter:
    @staticmethod
    def to_csv(data: List[Dict[str, Any]], filename: str):
        if not data:
            return
        
        save_path = settings.DOWNLOADS_DIR / "data" / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        keys = data[0].keys()
        with open(save_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
            
    @staticmethod
    def to_json(data: Any, filename: str):
        save_path = settings.DOWNLOADS_DIR / "data" / filename
        print(f"DEBUG: Attempting to save JSON to {save_path}")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"DEBUG: Successfully saved {save_path}")
