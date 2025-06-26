#!/usr/bin/env python3
"""
Test the fixed JSON extraction with the problematic cases.
"""

import json
import logging
from internvl.extraction.json_extraction_fixed import extract_json_from_text
from internvl.utils.logging import setup_logging

# Setup logging
setup_logging(logging.DEBUG)

# The exact problematic output from your model
model_output_sample = '''```json
{
  "company_name": "WOOLWORTHS",
  "address": "123 Main St
             Sydney NSW 2000",
  "phone_number": "(02) 1234 5678",
  "date": "15/06/2024
  "
}
```'''

control_char_sample = '''```json
{
  "company_name": "COLES\x08\x0b",
  "address": "456 High St", 
  "phone_number": "0412345678",
  "date": "16/06/2024",
  "total_amount": 23.45
}
```'''

def test_fixed_extraction():
    """Test the fixed extraction method."""
    print("Testing FIXED JSON extraction...")
    
    test_cases = [
        ("Model output with newlines", model_output_sample),
        ("Control characters", control_char_sample),
    ]
    
    for name, test_input in test_cases:
        print(f"\n--- {name} ---")
        print(f"Input: {repr(test_input[:80])}...")
        
        try:
            result = extract_json_from_text(test_input)
            print("SUCCESS: Extracted JSON:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_fixed_extraction()