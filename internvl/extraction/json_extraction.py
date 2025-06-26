"""
JSON extraction utilities for InternVL Evaluation

This module provides functions for extracting JSON from model output text.
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
                cleaned_json = _clean_and_fix_json(potential_json.strip())
                logger.debug(f"Original JSON:\n{potential_json.strip()}")
                logger.debug(f"Cleaned JSON:\n{cleaned_json}")
                try:
                    result = json.loads(cleaned_json)
                    logger.info("Successfully parsed JSON after cleaning")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed after cleaning: {e}")
                    continue

        # If markdown format failed, try general JSON pattern
        json_pattern = r"({[\s\S]*?})"
        matches = re.findall(json_pattern, text)

        for potential_json in matches:
            cleaned_json = _clean_and_fix_json(potential_json)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                continue
                
    except Exception as e:
        logger.error(f"Error extracting JSON from text: {e}")

    return default_json


def _clean_and_fix_json(json_text: str) -> str:
    """
    Clean and fix common JSON formatting issues from model output.
    
    Args:
        json_text: Raw JSON text that may have formatting issues
        
    Returns:
        Cleaned JSON text
    """
    # Remove leading/trailing whitespace
    cleaned = json_text.strip()
    
    # CRITICAL: Remove actual control characters that cause "Invalid control character" errors
    # Replace actual newlines with \n in the text first
    import string
    printable = set(string.printable)
    cleaned = ''.join(c if c in printable else ' ' for c in cleaned)
    
    # Fix the orphaned comma pattern specifically: ",\n  ",
    cleaned = re.sub(r'",\s*\n\s*",\s*\n', '",\n', cleaned)
    
    # Fix orphaned commas on their own lines (very common in this model's output)
    cleaned = re.sub(r'\n\s*",\s*\n', ',\n', cleaned)
    
    # Fix lines that are just commas with whitespace
    cleaned = re.sub(r'\n\s*,\s*\n', '\n', cleaned)
    
    # Fix pattern: "value"\n  " (unclosed quote with newline)
    cleaned = re.sub(r':\s*"([^"]*?)\s*\n\s*"\s*,?\s*\n', r': "\1",\n', cleaned)
    
    # Fix unclosed quotes at end of JSON values (before closing brace)
    cleaned = re.sub(r':\s*"([^"]*?)\s*\n\s*"\s*\n\s*}', r': "\1"\n}', cleaned)
    
    # Fix missing commas between fields - improved pattern
    cleaned = re.sub(r'"\s*\n\s*"([^"]+)":', r'",\n  "\1":', cleaned)
    
    # Fix missing commas between numeric/string values and next key
    cleaned = re.sub(r'(\d+|\w+)\s*\n\s*"([^"]+)":', r'\1,\n  "\2":', cleaned)
    
    # Fix unescaped actual newlines in quoted strings
    def fix_newlines_in_quoted_strings(match):
        key = match.group(1)
        value = match.group(2)
        # Replace actual newlines with \n
        value = value.replace('\n', '\\n').replace('\r', '\\r')
        return f'"{key}": "{value}"'
    
    # Apply to quoted string values that contain actual newlines
    cleaned = re.sub(r'"([^"]+)":\s*"([^"]*\n[^"]*)"', fix_newlines_in_quoted_strings, cleaned)
    
    # Fix addresses with multiple unquoted lines
    # Pattern: "address": "Line1\n             Line2",
    cleaned = re.sub(r'("address":\s*"[^"]*?)\n\s*([^",\n}]+?)\n\s*([^",\n}]+?)"', 
                    lambda m: f'{m.group(1)}\\n{m.group(2).strip()}\\n{m.group(3).strip()}"', 
                    cleaned)
    
    # Fix single quotes to double quotes
    cleaned = cleaned.replace("'", '"')
    
    # Fix unquoted keys
    cleaned = re.sub(r'(\s*?)([a-zA-Z_][a-zA-Z0-9_]*)(\s*?):', r'\1"\2"\3:', cleaned)
    
    # Remove trailing commas before closing braces
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Last resort: try to salvage severely malformed JSON by reconstructing it
    if not _is_valid_json_structure(cleaned):
        cleaned = _reconstruct_json(cleaned)
    
    return cleaned


def _is_valid_json_structure(text: str) -> bool:
    """Check if text has basic JSON structure."""
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def _reconstruct_json(malformed_json: str) -> str:
    """
    Last resort: reconstruct JSON from severely malformed output.
    This handles cases where the model completely botches the format.
    """
    logger.info("Attempting JSON reconstruction as last resort")
    
    # Initialize with expected fields for receipt extraction
    expected_fields = {
        "company_name": "",
        "address": "",
        "phone_number": "",
        "date": "",
        "ABN": "",
        "total_amount": ""
    }
    
    # More aggressive pattern matching for key-value extraction
    # Look for various patterns that might represent key-value pairs
    patterns = [
        r'"([^"]+)"\s*:\s*"([^"]*)"',  # "key": "value"
        r'"([^"]+)"\s*:\s*([^,\n}]+)',  # "key": value
        r'([a-zA-Z_]+)\s*:\s*"([^"]*)"',  # key: "value"
        r'([a-zA-Z_]+)\s*:\s*([^,\n}]+)',  # key: value
    ]
    
    extracted_pairs = {}
    
    for pattern in patterns:
        matches = re.findall(pattern, malformed_json)
        for key, value in matches:
            # Clean the key
            key = key.strip().lower().replace(' ', '_')
            
            # Map common variations to standard field names
            key_mappings = {
                'company': 'company_name',
                'store': 'company_name',
                'business': 'company_name',
                'phone': 'phone_number',
                'tel': 'phone_number',
                'telephone': 'phone_number',
                'total': 'total_amount',
                'amount': 'total_amount',
                'price': 'total_amount',
            }
            
            # Apply key mapping
            for variant, standard in key_mappings.items():
                if variant in key:
                    key = standard
                    break
            
            # Clean the value
            value = value.strip()
            
            # Remove trailing quotes, newlines, and extra whitespace
            value = re.sub(r'["\']\s*$', '', value)
            value = re.sub(r'\s*\n.*$', '', value, flags=re.DOTALL)
            value = value.strip()
            
            # Only keep non-empty values and valid field names
            if value and key in expected_fields:
                extracted_pairs[key] = value
    
    # Build the reconstructed JSON
    reconstructed = "{\n"
    pairs_added = 0
    
    for field in expected_fields:
        if field in extracted_pairs:
            value = extracted_pairs[field]
            
            # Format the value appropriately
            if value.replace('.', '').replace('$', '').replace(',', '').isdigit():
                # Numeric value - remove quotes and currency symbols
                value = value.replace('$', '').replace(',', '')
                if '.' in value:
                    value = str(float(value))
                else:
                    value = str(int(value))
            else:
                # String value - ensure it's quoted and escape newlines
                value = value.replace('\n', '\\n').replace('\r', '\\r')
                if not value.startswith('"'):
                    value = f'"{value}"'
            
            comma = "," if pairs_added < len(extracted_pairs) - 1 else ""
            reconstructed += f'  "{field}": {value}{comma}\n'
            pairs_added += 1
    
    reconstructed += "}"
    
    logger.debug(f"Reconstructed JSON with {pairs_added} fields:\n{reconstructed}")
    return reconstructed


def extract_json_from_response(
    output: str, extraction_pattern: str = r'{\s*"(date|store|tax|total|prod).*?}'
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
