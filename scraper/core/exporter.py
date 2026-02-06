import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class Exporter:
    @staticmethod
    def to_csv(data: List[Dict], filepath: str):
        """
        Exports a list of dictionaries to CSV, strictly following the user's DB schema.
        """
        if not data:
            logger.warning("No data to export to CSV.")
            return

        # Defined Schema Columns
        db_columns = [
            "id", "run_id", "row_id", "title", "description", "source", "category", 
            "link", "image_url", "status", "scheduled_at", "created_at", "updated_at", 
            "likes", "content", "slug", "excerpt", "meta_title", "meta_description", 
            "meta_keywords", "canonical_url", "og_title", "og_description", "og_image", 
            "focus_keyword", "is_indexable", "is_followable", "images"
        ]

        formatted_data = []
        now = datetime.now()

        for item in data:
            # Map scraper keys to DB columns
            # Default Scraper Keys: title, short_description, sub_category, source_url, author, image_url
            row = {
                "id": None,
                "run_id": None,
                "row_id": None,
                "title": item.get("title"),
                "description": item.get("short_description"),
                "source": item.get("author", "System"),
                "category": item.get("sub_category", "General"),
                "link": item.get("source_url"),
                "image_url": item.get("image_url"),
                "status": "published",
                "scheduled_at": None,
                "created_at": now,
                "updated_at": now,
                "likes": 0,
                "content": item.get("short_description"), # Fallback to description as content
                "slug": None,
                "excerpt": None,
                "meta_title": item.get("title"),
                "meta_description": item.get("short_description"),
                "meta_keywords": None,
                "canonical_url": None,
                "og_title": None,
                "og_description": None,
                "og_image": item.get("image_url"),
                "focus_keyword": None,
                "is_indexable": True,
                "is_followable": True,
                "images": None
            }
            formatted_data.append(row)

        try:
            # Ensure directory exists if specified
            directory = os.path.dirname(filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # Create DataFrame with strict column order
            df = pd.DataFrame(formatted_data, columns=db_columns)
            
            # Export with NULL for missing values to match the user's example format
            df.to_csv(filepath, index=False, encoding='utf-8', na_rep='NULL')
            logger.info(f"Successfully exported {len(data)} items to {filepath} matching DB schema.")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")

    @staticmethod
    def to_json(data: List[Dict], filepath: str):
        """
        Exports a list of dictionaries to JSON.
        """
        if not data:
            logger.warning("No data to export to JSON.")
            return

        try:
             # Ensure directory exists if specified
            directory = os.path.dirname(filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Successfully exported {len(data)} items to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
