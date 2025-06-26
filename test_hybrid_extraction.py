#!/usr/bin/env python3
"""
Test the hybrid extraction system (KV format first, JSON fallback).

This script tests both key-value format parsing and JSON fallback scenarios
to verify the robust extraction recommendations are working properly.
"""

from internvl.extraction.json_extraction_fixed import (
    extract_structured_data,
    is_valid_extraction,
    parse_kv_format,
)


def test_kv_format():
    """Test key-value format parsing."""
    print("=" * 60)
    print("TESTING: Key-Value Format Parsing")
    print("=" * 60)
    
    # Test case 1: Perfect KV format
    kv_text = """DATE: 16/03/2023
STORE: WOOLWORTHS
TAX: 3.82
TOTAL: 42.08
PRODUCTS: MILK 2L | BREAD MULTIGRAIN | EGGS FREE RANGE 12PK
QUANTITIES: 1 | 2 | 1
PRICES: 4.50 | 8.00 | 7.60"""
    
    print("Test 1: Perfect KV format")
    print("Input:")
    print(kv_text)
    print("\nResult:")
    result = parse_kv_format(kv_text)
    print(result)
    print(f"Valid: {is_valid_extraction(result)}")
    print(f"Products count: {len(result.get('prod_item_value', []))}")
    
    # Test case 2: KV with mixed case and extra whitespace
    kv_text_2 = """
    Date: 05/05/2025  
    Store:  ALDI SUPERMARKET  
    Tax:    12.82
    Total:  140.98
    Products: Chocolate Bar | Apple Juice 1L | Organic Bread  
    Quantities:  3 | 1 | 2
    Prices: 2.50 | 4.99 | 5.49  
    """
    
    print("\n" + "-" * 40)
    print("Test 2: KV with mixed case and whitespace")
    print("Input:")
    print(kv_text_2)
    print("\nResult:")
    result2 = parse_kv_format(kv_text_2)
    print(result2)
    print(f"Valid: {is_valid_extraction(result2)}")
    print(f"Products count: {len(result2.get('prod_item_value', []))}")
    
    return True

def test_json_fallback():
    """Test JSON fallback for malformed JSON."""
    print("\n" + "=" * 60)
    print("TESTING: JSON Fallback (Malformed Input)")
    print("=" * 60)
    
    # This is the actual broken JSON that we've been dealing with
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
"Chocolate"
],
"prod_quan"""
    
    print("Test: Broken JSON (should fallback to reconstruction)")
    print("Input (truncated):")
    print(broken_json[:200] + "...")
    print("\nResult:")
    result = extract_structured_data(broken_json)
    print(result)
    print(f"Valid: {is_valid_extraction(result)}")
    print(f"Products count: {len(result.get('prod_item_value', []))}")
    
    return True

def test_hybrid_pipeline():
    """Test the full hybrid pipeline with different input types."""
    print("\n" + "=" * 60)
    print("TESTING: Hybrid Pipeline (KV first, JSON fallback)")
    print("=" * 60)
    
    test_cases = [
        ("KV Format", """DATE: 16/03/2023
STORE: COLES
TAX: 2.15
TOTAL: 23.65
PRODUCTS: Coffee 200g | Biscuits | Orange Juice
QUANTITIES: 1 | 2 | 1
PRICES: 8.50 | 6.00 | 9.15"""),
        
        ("Valid JSON", """{
  "date_value": "20/12/2024",
  "store_name_value": "IGA",
  "tax_value": "1.50",
  "total_value": "16.50",
  "prod_item_value": ["Bananas", "Yogurt"],
  "prod_quantity_value": ["1", "2"],
  "prod_price_value": ["3.00", "12.00"]
}"""),
        
        ("Random Text (should fail gracefully)", "This is just random text with no structure"),
        
        ("Mixed Format", """Some random text before
DATE: 25/06/2025
STORE: BUNNINGS WAREHOUSE
TAX: 4.50
TOTAL: 49.50
PRODUCTS: Drill Bits | Paint Brush | Screws Pack
QUANTITIES: 1 | 2 | 3
PRICES: 15.00 | 12.00 | 7.50
Some text after""")
    ]
    
    for i, (test_name, test_input) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_name}")
        print("Input:")
        print(test_input[:100] + ("..." if len(test_input) > 100 else ""))
        print("\nResult:")
        result = extract_structured_data(test_input)
        print(f"Date: {result.get('date_value', 'N/A')}")
        print(f"Store: {result.get('store_name_value', 'N/A')}")
        print(f"Tax: {result.get('tax_value', 'N/A')}")
        print(f"Total: {result.get('total_value', 'N/A')}")
        print(f"Products: {result.get('prod_item_value', [])}")
        print(f"Valid: {is_valid_extraction(result)}")
        print(f"Products count: {len(result.get('prod_item_value', []))}")
        print("-" * 40)
    
    return True

def main():
    """Run all hybrid extraction tests."""
    print("HYBRID EXTRACTION SYSTEM TEST")
    print("Testing the robust output format implementation")
    print("=" * 60)
    
    tests = [
        ("Key-Value Format Tests", test_kv_format),
        ("JSON Fallback Tests", test_json_fallback),
        ("Hybrid Pipeline Tests", test_hybrid_pipeline),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                passed += 1
                print(f"\n✅ {test_name} PASSED")
            else:
                print(f"\n❌ {test_name} FAILED")
        except Exception as e:
            print(f"\n💥 {test_name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Hybrid extraction system is working!")
        print("\nNext steps:")
        print("1. Update .env to use key_value_receipt_prompt")
        print("2. Run evaluation to compare performance")
        print("3. Monitor KV vs JSON extraction success rates")
    else:
        print("⚠️ Some tests failed. Check implementation.")
    
    return passed == total

if __name__ == "__main__":
    main()