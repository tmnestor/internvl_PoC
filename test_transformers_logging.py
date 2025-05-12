#!/usr/bin/env python3
"""
Test script to verify transformers logging configuration works correctly
"""

import logging
from src.internvl.utils.logging import setup_logging, setup_transformers_logging

# First set up normal application logging
print("Setting up application logging...")
setup_logging(level=logging.INFO)

# Now import transformers and test the warning suppression
print("Testing transformers logging suppression...")
try:
    from transformers import AutoTokenizer, logging as transformers_logging
    
    # Get current verbosity 
    print(f"Current transformers verbosity: {transformers_logging.get_verbosity()}")
    
    # Explicitly set transformers logging
    print("Setting transformers logging to WARNING level...")
    setup_transformers_logging(logging.WARNING)
    
    # Check level after our call
    print(f"New transformers verbosity: {transformers_logging.get_verbosity()}")
    
    # Test loading a tokenizer (which produces the warning we want to suppress)
    print("Loading a test tokenizer (should not see pad_token_id warning)...")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    print("Test completed successfully!")
except ImportError:
    print("Transformers library not installed. Please install with 'pip install transformers'")
    