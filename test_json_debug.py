#!/usr/bin/env python3
"""
Test script for debugging JSON extraction issues with control characters.
"""

import json
import logging

from internvl.extraction.json_extraction import extract_json_from_text
from internvl.utils.logging import setup_logging

# Setup logging to see debug output
setup_logging(logging.DEBUG)

# Test cases with problematic control characters that cause "Invalid control character" errors
test_cases = [
    # Case 1: Simple malformed JSON with control characters
    '''```json
{
  "company_name": "WOOLWORTHS",
  "address": "123 Main St
             Sydney NSW 2000",
  "phone_number": "(02) 1234 5678",
  "date": "15/06/2024
  "
}
```''',
    
    # Case 2: JSON with embedded control characters (simulated)
    '''```json
{
  "company_name": "COLES\x08\x0b",
  "address": "456 High St",
  "phone_number": "0412345678",
  "date": "16/06/2024",
  "total_amount": 23.45
}
```''',
    
    # Case 3: The problematic pattern from actual model output
    '''```json
{
  "company_name": "WOOLWORTHS",
  "address": "Shop 1, 123 Main Street
  "
}
```''',
]

def test_json_extraction():
    """Test the enhanced JSON extraction with problematic inputs."""
    print("Testing enhanced JSON extraction with problematic control characters...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {repr(test_case[:100])}...")
        
        try:
            result = extract_json_from_text(test_case)
            print(f"SUCCESS: Extracted JSON: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_json_extraction()