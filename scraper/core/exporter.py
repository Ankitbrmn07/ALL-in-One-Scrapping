import pandas as pd
import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class Exporter:
    @staticmethod
    def to_csv(data: List[Dict], filepath: str):
        """
        Exports a list of dictionaries to CSV.
        """
        if not data:
            logger.warning("No data to export to CSV.")
            return

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
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
             # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Successfully exported {len(data)} items to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
