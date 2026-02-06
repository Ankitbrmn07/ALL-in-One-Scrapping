import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)

from scraper.core.exporter import Exporter

def test_exporter_schema():
    print("Testing Exporter Schema...")
    
    # Dummy data simulating scraper output
    dummy_data = [{
        "title": "Test Article",
        "short_description": "This is a test description.",
        "sub_category": "Cricket",
        "source_url": "http://example.com/article",
        "author": "ESPN",
        "image_url": "http://example.com/image.jpg"
    }]
    
    output_file = "test_schema_output.csv"
    
    # Run export
    Exporter.to_csv(dummy_data, output_file)
    
    # Verify Metadata
    if os.path.exists(output_file):
        print(f"File {output_file} created.")
        
        df = pd.read_csv(output_file)
        
        # Check Columns
        expected_columns = [
            "id", "run_id", "row_id", "title", "description", "source", "category", 
            "link", "image_url", "status", "scheduled_at", "created_at", "updated_at", 
            "likes", "content", "slug", "excerpt", "meta_title", "meta_description", 
            "meta_keywords", "canonical_url", "og_title", "og_description", "og_image", 
            "focus_keyword", "is_indexable", "is_followable", "images"
        ]
        
        columns_match = list(df.columns) == expected_columns
        print(f"Columns Match: {columns_match}")
        if not columns_match:
            print("Expected:", expected_columns)
            print("Got:", list(df.columns))
            
        # Check Data Mapping
        row = df.iloc[0]
        print(f"Title: {row['title']} (Expected: Test Article)")
        print(f"Description: {row['description']} (Expected: This is a test description.)")
        print(f"Source: {row['source']} (Expected: ESPN)")
        print(f"Status: {row['status']} (Expected: published)")
        print(f"Created At: {row['created_at']}")
        
        # Check Defaults (NULLs) -> Pandas reads NULL as NaN by default, but we wrote 'NULL' string?
        # If we used na_rep='NULL', then empty fields in input became 'NULL' string in CSV.
        # But wait, pd.read_csv might interpret 'NULL' as NaN if we don't tell it not to.
        # Let's inspect the raw file content to be sure.
        
        with open(output_file, 'r') as f:
            content = f.read()
            print("\nRaw CSV Content Sample:")
            print(content[:500])
             
    else:
        print("Export failed, file not found.")

if __name__ == "__main__":
    test_exporter_schema()
