#!/usr/bin/env python3
"""
Test the JSON extraction fix with the actual problematic output from the model.
"""

from internvl.extraction.json_extraction_fixed import extract_json_from_text

# This is the actual broken output from the diagnostic
broken_json = """{
"date_value": "05/05/2025",
"store_name_value": "WOOLWORTHS",
"tax_value": "12.82,
"total_value": "140.98,
"prod_item_value": [
"Milk 2L,
"Chicken Breast,
"Rice 1kg,
"Bread,
"Chocolate
],
"prod_quan"""

print("Testing JSON extraction fix...")
print(f"Original broken JSON ({len(broken_json)} chars):")
print(broken_json)
print("\n" + "="*60)

result = extract_json_from_text(broken_json)

print("Extraction result:")
print(result)
print(f"\nKeys extracted: {list(result.keys()) if result else 'None'}")

if result and "date_value" in result:
    print("✅ JSON extraction SUCCESSFUL!")
    print(f"Date: {result.get('date_value')}")
    print(f"Store: {result.get('store_name_value')}")
    print(f"Tax: {result.get('tax_value')}")
    print(f"Total: {result.get('total_value')}")
    print(f"Products: {result.get('prod_item_value', [])}")
else:
    print("❌ JSON extraction FAILED!")