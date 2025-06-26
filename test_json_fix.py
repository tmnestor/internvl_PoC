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

# Also test a simpler case
simple_broken = """{"date_value": "05/05/2025","store_name_value": "WOOLWORTHS","tax_value": "12.82,"""

def test_extraction(test_name, test_json):
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"Input ({len(test_json)} chars):")
    print(test_json)
    print("\n" + "-"*40)

    result = extract_json_from_text(test_json)

    print("Extraction result:")
    print(result)
    print(f"\nKeys extracted: {list(result.keys()) if result else 'None'}")

    if result and result.get('date_value'):
        print("✅ JSON extraction SUCCESSFUL!")
        print(f"Date: '{result.get('date_value')}'")
        print(f"Store: '{result.get('store_name_value')}'")
        print(f"Tax: '{result.get('tax_value')}'")
        print(f"Total: '{result.get('total_value')}'")
        print(f"Products: {result.get('prod_item_value', [])}")
        print(f"Product count: {len(result.get('prod_item_value', []))}")
        return True
    else:
        print("❌ JSON extraction FAILED!")
        return False

print("Testing enhanced JSON extraction with aggressive reconstruction...")

# Test cases
success_count = 0
total_tests = 2

success_count += test_extraction("Complex Broken JSON (Real Model Output)", broken_json)
success_count += test_extraction("Simple Broken JSON", simple_broken)

print(f"\n{'='*60}")
print(f"SUMMARY: {success_count}/{total_tests} tests passed")

if success_count == total_tests:
    print("🎉 All tests passed! JSON reconstruction is working!")
else:
    print("⚠️  Some tests failed. JSON reconstruction needs more work.")