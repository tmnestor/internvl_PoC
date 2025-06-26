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
    
    # Fix the specific pattern: "value",\n  "next_key" - remove orphaned commas
    cleaned = re.sub(r'",\s*\n\s*",', '",', cleaned)
    
    # Fix orphaned commas on their own lines
    cleaned = re.sub(r'",\s*\n\s*,\s*\n', '",\n', cleaned)
    
    # Fix lines that are just commas with whitespace
    cleaned = re.sub(r'\n\s*,\s*\n', '\n', cleaned)
    
    # Fix unclosed quotes at end of values (very common pattern)
    # Pattern: "key": "value\n" should be "key": "value",
    cleaned = re.sub(r':\s*"([^"]*?)\s*\n\s*"', r': "\1"', cleaned)
    
    # Fix missing commas between key-value pairs
    # Pattern: "value"\n  "next_key": becomes "value",\n  "next_key":
    cleaned = re.sub(r'"\s*\n\s*"([^"]+)":', r'",\n  "\1":', cleaned)
    
    # Fix missing commas between numeric values and next key
    # Pattern: 123\n  "next_key": becomes 123,\n  "next_key":
    cleaned = re.sub(r'(\d+)\s*\n\s*"([^"]+)":', r'\1,\n  "\2":', cleaned)
    
    # Fix unescaped newlines in string values
    def fix_newlines_in_strings(match):
        content = match.group(1)
        content = content.replace('\n', '\\n')
        return f'"{content}"'
    
    # Apply newline fixing to quoted strings that span multiple lines
    cleaned = re.sub(r'"([^"]*\n[^"]*)"', fix_newlines_in_strings, cleaned)
    
    # Fix pattern where address has multiple lines with extra quotes
    # "address": "Line1\n             Line2\n             Line3",
    cleaned = re.sub(r'"([^"]*?)"\s*\n\s*([^",\n}]+?)\s*\n\s*([^",\n}]+?)"', 
                    lambda m: f'"{m.group(1)}\\n{m.group(2).strip()}\\n{m.group(3).strip()}"', 
                    cleaned)
    
    # Fix missing quotes around multi-line values
    # Pattern: "key": value1\n             value2",
    cleaned = re.sub(r':\s*([^",\n{]+?)\s*\n\s*([^",\n}]+?)"', r': "\1\\n\2"', cleaned)
    
    # Fix single quotes to double quotes
    cleaned = cleaned.replace("'", '"')
    
    # Fix unquoted keys
    cleaned = re.sub(r'(\s*?)([a-zA-Z_][a-zA-Z0-9_]*)(\s*?):', r'\1"\2"\3:', cleaned)
    
    # Remove trailing commas before closing braces
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Final cleanup - fix any remaining unclosed quotes at the end
    # Pattern: "total_amount": "88.06\n}
    cleaned = re.sub(r':\s*"([^"]*?)\s*\n\s*}', r': "\1"\n}', cleaned)
    
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
    
    # Extract potential key-value pairs using regex
    reconstructed = "{\n"
    
    # Look for patterns like: "key": "value" or "key": value
    pairs = re.findall(r'"([^"]+)"\s*:\s*([^,\n}]+)', malformed_json)
    
    for i, (key, value) in enumerate(pairs):
        # Clean the value
        value = value.strip()
        
        # Remove trailing quotes and newlines
        value = re.sub(r'["\']\s*$', '', value)
        value = re.sub(r'\s*\n.*$', '', value, flags=re.DOTALL)
        
        # Add quotes around string values if they don't have them
        if not (value.startswith('"') or value.replace('.', '').isdigit()):
            value = f'"{value}"'
        
        # Add the pair
        comma = "," if i < len(pairs) - 1 else ""
        reconstructed += f'  "{key}": {value}{comma}\n'
    
    reconstructed += "}"
    
    logger.debug(f"Reconstructed JSON:\n{reconstructed}")
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
