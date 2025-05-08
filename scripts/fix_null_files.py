#!/usr/bin/env python3
"""
Quick script to fix null JSON files
"""

import json
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.absolute()

# List of problematic files
problem_files = [
    "data/sroie/ground_truth/sroie_test_002.json",
    "data/sroie/ground_truth/sroie_test_005.json",
    "data/sroie/ground_truth/sroie_test_023.json"
]

# Empty template
empty_template = {
    "date_value": "",
    "store_name_value": "",
    "tax_value": "",
    "total_value": "",
    "prod_item_value": [],
    "prod_quantity_value": [],
    "prod_price_value": []
}

# Fix each file
for file_path in problem_files:
    path = project_root / file_path
    if path.exists():
        with open(path, 'w') as f:
            json.dump(empty_template, f, indent=2)
        print(f"Fixed {path.name}")
    else:
        print(f"File not found: {path}")

print("Finished fixing null files")