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
                try:
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
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
    
    # Fix missing commas between fields (common issue)
    # Look for patterns like: "value"\n  "next_key" and add comma
    cleaned = re.sub(r'"\s*\n\s*"([^"]+)":', r'",\n  "\1":', cleaned)
    
    # Fix missing commas before closing quotes
    # Look for patterns like: value"\n} and add comma
    cleaned = re.sub(r'([^,])\s*"\s*\n\s*}', r'\1"\n}', cleaned)
    
    # Fix unescaped newlines in string values
    # Replace actual newlines with \n in quoted strings
    def fix_newlines_in_strings(match):
        content = match.group(1)
        # Replace literal newlines with escaped newlines
        content = content.replace('\n', '\\n')
        return f'"{content}"'
    
    # Apply newline fixing to quoted strings
    cleaned = re.sub(r'"([^"]*\n[^"]*)"', fix_newlines_in_strings, cleaned)
    
    # Fix unclosed quotes at end of values
    # Look for patterns like: "value and add closing quote
    cleaned = re.sub(r':\s*"([^"\n]+)\s*\n', r': "\1",\n', cleaned)
    
    # Fix single quotes to double quotes
    cleaned = cleaned.replace("'", '"')
    
    # Fix unquoted keys
    cleaned = re.sub(r'(\s*?)([a-zA-Z_][a-zA-Z0-9_]*)(\s*?):', r'\1"\2"\3:', cleaned)
    
    # Remove trailing commas before closing braces
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Fix missing quotes around string values that contain spaces
    # This is a more aggressive fix - only apply if standard parsing fails
    
    return cleaned


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
