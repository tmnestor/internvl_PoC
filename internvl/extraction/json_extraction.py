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
    Extract JSON object from model output text.

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
                try:
                    return json.loads(potential_json.strip())
                except json.JSONDecodeError:
                    continue

        # If markdown format failed, try general JSON pattern
        json_pattern = r"({[\s\S]*?})"
        matches = re.findall(json_pattern, text)

        for potential_json in matches:
            try:
                # Try to parse the JSON
                return json.loads(potential_json)
            except json.JSONDecodeError:
                # If that fails, try to fix common issues
                try:
                    # Fix single quotes to double quotes
                    fixed_json = potential_json.replace("'", '"')
                    # Fix unquoted keys
                    fixed_json = re.sub(r"(\s*?)(\w+)(\s*?):", r'\1"\2"\3:', fixed_json)
                    return json.loads(fixed_json)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.error(f"Error extracting JSON from text: {e}")

    return default_json


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
