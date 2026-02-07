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
        Exports a list of dictionaries to CSV. 
        Detects if property schema or DB schema should be used.
        """
        if not data:
            logger.warning("No data to export to CSV.")
            return

        # Check if it should use Property Schema (based on user request)
        property_keys = ["Serial", "Title", "Type", "Amenities", "Price", "Address", "Images", "Description", "Summary", "Source", "Extra"]
        if all(k in data[0] for k in ["Serial", "Price", "Address"]):
            logger.info(f"Exporter: Using Property Schema for {filepath}")
            # Ensure columns are in the requested order and filtered to requested ones
            formatted_data = []
            for item in data:
                row = {k: item.get(k, "N/A") for k in property_keys}
                formatted_data.append(row)
            df = pd.DataFrame(formatted_data, columns=property_keys)
        else:
            # Mandatory 28-field Schema
            db_columns = [
                "id", "run_id", "row_id", "title", "description", "source", "category",
                "link", "image_url", "status", "scheduled_at", "created_at", "updated_at",
                "likes", "content", "slug", "excerpt", "meta_title", "meta_description",
                "meta_keywords", "canonical_url", "og_title", "og_description", "og_image",
                "focus_keyword", "is_indexable", "is_followable", "images"
            ]

            formatted_data = []
            now = datetime.now().isoformat()

            for item in data:
                # Map scraper keys to the mandatory 28 fields
                row = {col: item.get(col, "") for col in db_columns}
                
                # Fill in defaults for mandatory but often missing fields
                if not row.get("status"): row["status"] = "published"
                if not row.get("created_at"): row["created_at"] = now
                if not row.get("updated_at"): row["updated_at"] = now
                if row.get("is_indexable") == "": row["is_indexable"] = True
                if row.get("is_followable") == "": row["is_followable"] = True
                if row.get("likes") == "": row["likes"] = 0
                
                # Fallback mapping for older keys if present
                if not row.get("title") and item.get("Title"): row["title"] = item["Title"]
                if not row.get("description") and item.get("Description"): row["description"] = item["Description"]
                if not row.get("link") and item.get("Source"): row["link"] = item["Source"]
                
                formatted_data.append(row)
            
            df = pd.DataFrame(formatted_data, columns=db_columns)

        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # Export with NULL for missing values
            df.to_csv(filepath, index=False, encoding='utf-8', na_rep='NULL')
            logger.info(f"Successfully exported {len(data)} items to {filepath}")
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
