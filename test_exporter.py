import sys
import os
import pandas as pd
import logging

sys.path.append(os.getcwd())
from scraper.core.exporter import Exporter

def test_export_property():
    logging.basicConfig(level=logging.INFO)
    data = [{
        "Serial": 1,
        "Title": "Test Price",
        "Price": "$1.2 million",
        "Address": "Vancouver, BC",
        "Amenities": "Pool",
        "Type": "Real Estate",
        "Images": "img1.jpg",
        "Description": "Desc",
        "Summary": "Sum",
        "Source": "url",
        "Extra": "{}"
    }]
    
    output = "test_property_export.csv"
    Exporter.to_csv(data, output)
    
    if os.path.exists(output):
        df = pd.read_csv(output)
        print("Generated Headers:", list(df.columns))
        print("Expected Headers: ['Serial', 'Title', 'Type', 'Amenities', 'Price', 'Address', 'Images', 'Description', 'Summary', 'Source', 'Extra']")
        
        # Verify content
        print("\nCSV Content:")
        print(df.to_string())
    else:
        print("Export failed!")

if __name__ == "__main__":
    test_export_property()
