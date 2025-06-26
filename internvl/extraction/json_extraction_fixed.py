"""
Fixed JSON extraction utilities for InternVL Evaluation

This module provides functions for extracting JSON from model output text with improved error handling.
"""

import json
import re
from typing import Any, Dict

from internvl.utils import get_logger

# Get logger for this module
logger = get_logger(__name__)


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON object from model output text with robust error handling.

    Args:
        text: Raw model output text

    Returns:
        Parsed JSON object
    """
    # Default structure for fallback
    default_json = {
        "date_value": "",
        "store_name_value": "",
        "tax_value": "",
        "total_value": "",
        "prod_item_value": [],
        "prod_quantity_value": [],
        "prod_price_value": [],
    }

    if not text:
        return default_json

    try:
        # First try to find JSON enclosed in triple backticks
        json_pattern = r"```(?:json)?(.*?)```"
        markdown_matches = re.findall(json_pattern, text, re.DOTALL)

        if markdown_matches:
            # Try each potential JSON block (prioritize longer ones)
            markdown_matches.sort(key=len, reverse=True)
            for potential_json in markdown_matches:
                original_json = potential_json.strip()
                logger.info(f"Processing JSON block of length {len(original_json)}")
                logger.debug(f"Original JSON:\n{repr(original_json)}")
                
                result = _try_parse_with_cleaning(original_json)
                if result is not None:
                    return result

        # If markdown format failed, try general JSON pattern
        json_pattern = r"({[\s\S]*?})"
        matches = re.findall(json_pattern, text)

        for potential_json in matches:
            result = _try_parse_with_cleaning(potential_json)
            if result is not None:
                return result
                
    except Exception as e:
        logger.error(f"Error extracting JSON from text: {e}")

    return default_json


def _try_parse_with_cleaning(json_text: str) -> Dict[str, Any]:
    """
    Try to parse JSON with progressive cleaning steps.
    
    Returns None if all attempts fail, otherwise returns parsed JSON.
    """
    # Step 1: Try parsing as-is
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        pass
    
    # Step 2: Ultra-aggressive character sanitization
    cleaned = _ultra_clean_json(json_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed after ultra-cleaning: {e}")
    
    # Step 3: REMOVED - No pattern reconstruction fallbacks
    # If JSON is malformed, we fail honestly rather than corrupt data
    logger.error(f"JSON parsing failed completely - malformed syntax from model")
    
    return None


def _ultra_clean_json(text: str) -> str:
    """
    Ultra-aggressive JSON cleaning to remove control characters and fix common issues.
    """
    # Step 1: Remove/replace problematic characters
    cleaned_chars = []
    control_chars_found = 0
    
    for char in text:
        char_code = ord(char)
        if char_code < 32:
            if char in '\t\n\r':
                cleaned_chars.append(char)
            else:
                cleaned_chars.append(' ')  # Replace control chars with space
                control_chars_found += 1
        elif char_code == 127:  # DEL
            cleaned_chars.append(' ')
            control_chars_found += 1
        else:
            cleaned_chars.append(char)
    
    if control_chars_found > 0:
        logger.warning(f"Replaced {control_chars_found} control characters with spaces")
    
    cleaned = ''.join(cleaned_chars)
    
    # Step 2: Fix common malformed patterns
    # Fix broken quotes: "value\n  " -> "value"
    cleaned = re.sub(r':\s*"([^"]*?)\s*\n\s*"\s*([,\n}])', r': "\1"\2', cleaned)
    
    # Fix missing quotes after commas
    cleaned = re.sub(r'",\s*\n\s*([a-zA-Z_][^"]*?):', r'",\n  "\1":', cleaned)
    
    # Fix orphaned commas
    cleaned = re.sub(r'\n\s*",\s*\n', ',\n', cleaned)
    
    # Remove trailing commas
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Clean up excessive whitespace
    cleaned = re.sub(r' +', ' ', cleaned)
    
    return cleaned


def _reconstruct_from_patterns(malformed_text: str) -> str:
    """
    Reconstruct valid JSON from malformed text using pattern matching.
    """
    logger.info("Attempting pattern-based JSON reconstruction")
    
    # Expected fields for SROIE schema (Australian receipts)
    fields = {
        "date_value": "",
        "store_name_value": "",
        "tax_value": "",
        "total_value": "",
        "prod_item_value": [],
        "prod_quantity_value": [],
        "prod_price_value": []
    }
    
    # Extract key-value pairs using multiple patterns
    patterns = [
        r'"([^"]+)"\s*:\s*"([^"]*?)"',  # Standard "key": "value"
        r'"([^"]+)"\s*:\s*([^,\n}]+)',  # "key": unquoted_value
        r'"([^"]+)"\s*:\s*"([^"]*?)(?:\s*\n[^"]*?)*"',  # Multiline values
    ]
    
    extracted = {}
    
    for pattern in patterns:
        matches = re.findall(pattern, malformed_text, re.DOTALL)
        for key, value in matches:
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            
            # Map common variations
            key_mappings = {
                'company': 'company_name',
                'store': 'company_name',
                'phone': 'phone_number',
                'total': 'total_amount',
            }
            
            for variant, standard in key_mappings.items():
                if variant in key:
                    key = standard
                    break
            
            if key in fields and value:
                # Clean the value
                value = re.sub(r'\s*\n.*$', '', value, flags=re.DOTALL)  # Remove trailing newlines
                value = value.strip()
                extracted[key] = value
                logger.debug(f"Extracted: {key} = {value}")
    
    # Build clean JSON
    json_parts = ["{"]
    field_count = 0
    
    for field in fields:
        if field in extracted:
            value = extracted[field]
            # Escape quotes and format as string
            value = value.replace('"', '\\"')
            comma = "," if field_count < len(extracted) - 1 else ""
            json_parts.append(f'  "{field}": "{value}"{comma}')
            field_count += 1
    
    json_parts.append("}")
    result = "\n".join(json_parts)
    
    logger.debug(f"Reconstructed JSON:\n{result}")
    return result


def extract_json_from_response(
    output: str, extraction_pattern: str = r'{\s*\"(date|store|tax|total|prod).*?}'
) -> Dict:
    """
    Extract and parse JSON output from the model's text response.

    Args:
        output: The raw text output from the model
        extraction_pattern: Regex pattern to find the JSON object

    Returns:
        The parsed JSON object containing the extracted fields
    """
    # Default parsed JSON to return in case of failure
    parsed_json = {
        "date_value": "",
        "store_name_value": "",
        "tax_value": "",
        "total_value": "",
        "prod_item_value": [],
        "prod_quantity_value": [],
        "prod_price_value": [],
    }

    try:
        # Search for JSON pattern in the response
        json_match = re.search(extraction_pattern, output, re.DOTALL)
        if json_match:
            # Extract and parse the JSON
            extracted_json = json_match.group(0)
            parsed_json = json.loads(extracted_json)
    except Exception as e:
        logger.error(f"LLM did not return a valid JSON format: {e}")

    # Always return parsed_json, whether default or extracted
    return parsed_json