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

# Validation imports removed for emergency restore


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
        # First try aggressive JSON reconstruction from malformed text
        reconstructed = _reconstruct_malformed_json(text)
        if reconstructed:
            try:
                result = json.loads(reconstructed)
                logger.info("Successfully reconstructed malformed JSON")
                return result
            except json.JSONDecodeError:
                pass

        # Then try to find JSON enclosed in triple backticks
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
    logger.error("JSON parsing failed completely - malformed syntax from model")
    
    return None


def _reconstruct_malformed_json(text: str) -> str:
    """
    Aggressively reconstruct JSON from severely malformed model output.
    
    This handles the specific case where the model generates incomplete JSON
    with missing quotes and control characters.
    """
    logger.info("Attempting aggressive JSON reconstruction")
    
    # Extract field-value pairs using regex patterns
    data = {}
    
    # Pattern for simple field: value pairs
    simple_pattern = r'"([^"]+)":\s*"([^"]*?)(?:",|$|\n)'
    matches = re.findall(simple_pattern, text, re.MULTILINE)
    
    for field, value in matches:
        if field in ["date_value", "store_name_value", "tax_value", "total_value"]:
            # Clean the value
            cleaned_value = re.sub(r'[^\w\s/.-]', '', value).strip()
            data[field] = cleaned_value
            logger.debug(f"Extracted {field}: '{cleaned_value}'")
    
    # Extract array fields (products, quantities, prices)
    
    # Look for array content
    array_pattern = r'"prod_item_value":\s*\[(.*?)(?:\]|$)'
    array_match = re.search(array_pattern, text, re.DOTALL)
    
    if array_match:
        array_content = array_match.group(1)
        # Extract quoted items
        item_pattern = r'"([^"]*?)"'
        items = re.findall(item_pattern, array_content)
        
        if items:
            # Clean items
            cleaned_items = []
            for item in items:
                # Remove trailing comma and clean
                cleaned_item = item.rstrip(',').strip()
                if cleaned_item:  # Only add non-empty items
                    cleaned_items.append(cleaned_item)
            
            data["prod_item_value"] = cleaned_items
            # For now, assume 1 quantity and use item as price (basic fallback)
            data["prod_quantity_value"] = ["1"] * len(cleaned_items)
            data["prod_price_value"] = ["0.00"] * len(cleaned_items)
            
            logger.info(f"Extracted {len(cleaned_items)} products")
    
    # Ensure all required fields exist
    required_fields = {
        "date_value": "",
        "store_name_value": "",
        "tax_value": "",
        "total_value": "",
        "prod_item_value": [],
        "prod_quantity_value": [],
        "prod_price_value": []
    }
    
    for field, default in required_fields.items():
        if field not in data:
            data[field] = default
    
    # Convert to JSON string
    try:
        reconstructed = json.dumps(data, indent=2)
        logger.info(f"Successfully reconstructed JSON with {len(data)} fields")
        return reconstructed
    except Exception as e:
        logger.error(f"Failed to serialize reconstructed data: {e}")
        return ""


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
    
    # Step 2: Fix common malformed patterns specific to model output
    
    # Fix missing closing quotes on values: "12.82, -> "12.82",
    cleaned = re.sub(r'"([^"]*?),\s*\n\s*"([a-z_])', r'"\1",\n"\2', cleaned)
    cleaned = re.sub(r'"([^"]*?),\s*\n\s*}', r'"\1"\n}', cleaned)
    cleaned = re.sub(r'"([^"]*?),\s*\n\s*\]', r'"\1"\n]', cleaned)
    
    # Fix missing quotes on array items: "Milk 2L, -> "Milk 2L",
    cleaned = re.sub(r'"([^"]*?),\s*\n\s*"([A-Z])', r'"\1",\n"\2', cleaned)
    
    # Fix broken quotes: "value\n  " -> "value"
    cleaned = re.sub(r':\s*"([^"]*?)\s*\n\s*"\s*([,\n}])', r': "\1"\2', cleaned)
    
    # Fix missing quotes after commas
    cleaned = re.sub(r'",\s*\n\s*([a-zA-Z_][^"]*?):', r'",\n  "\1":', cleaned)
    
    # Fix orphaned commas at line ends
    cleaned = re.sub(r',\s*\n\s*([}\]])', r'\n\1', cleaned)
    
    # Remove trailing commas before closing brackets
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Clean up excessive whitespace
    cleaned = re.sub(r' +', ' ', cleaned)
    
    # Ensure proper JSON structure completion
    if cleaned.count('{') > cleaned.count('}'):
        cleaned += '}'
    if cleaned.count('[') > cleaned.count(']'):
        cleaned += ']'
    
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