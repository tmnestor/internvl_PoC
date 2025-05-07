#!/usr/bin/env python3
"""
Quick script to fix the JSON field mapping for SROIE ground truth files
"""

import json
import glob
from pathlib import Path

# Directory containing the split ground truth files
ground_truth_dir = Path('raechel_gold_images/ground_truth')

# Process each file
for json_file in ground_truth_dir.glob('*.json'):
    try:
        # Read the current JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Check if we need to update the format
        if 'prod_item_value' in data:
            # Already in the correct format
            print(f"File {json_file.name} already in correct format")
            continue
        
        # Create the expected field structure
        updated_data = {
            "date_value": data.get("date_value", ""),
            "store_name_value": data.get("store_name_value", ""),
            "tax_value": data.get("tax_value", ""),
            "total_value": data.get("total_value", ""),
            "prod_item_value": data.get("items", []) or [],
            "prod_quantity_value": data.get("quantities", []) or [],
            "prod_price_value": data.get("prices", []) or []
        }
        
        # Save the updated JSON
        with open(json_file, 'w') as f:
            json.dump(updated_data, f, indent=2)
        
        print(f"Updated {json_file.name}")
    
    except Exception as e:
        print(f"Error processing {json_file.name}: {e}")

print("Finished updating JSON files")