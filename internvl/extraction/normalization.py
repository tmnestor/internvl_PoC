"""
Field normalization utilities for InternVL Evaluation

This module provides functions for normalizing field values extracted from model output.
"""

import re
from typing import Any, Dict

import dateparser

from internvl.extraction.json_extraction_fixed import extract_json_from_text
from internvl.utils import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Confidence scoring imports temporarily removed for emergency restore


def normalize_date(date_str: str) -> str:
    """
    Normalize dates to a standard format.

    Args:
        date_str: Input date string

    Returns:
        Normalized date string in DD/MM/YYYY format or original if parsing fails
    """
    try:
        # Remove any 'time' component if it exists (separated by space)
        if " " in date_str and not any(
            x in date_str.lower()
            for x in [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ]
        ):
            date_str = date_str.split(" ")[0]

        # Parse the date
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            # Format to DD/MM/YYYY
            return parsed_date.strftime("%d/%m/%Y")
        return date_str
    except Exception as e:
        logger.error(f"Error normalizing date '{date_str}': {e}")
        return date_str


def normalize_store_name(name_str: str) -> str:
    """
    Normalize store names to uppercase.

    Args:
        name_str: Input store name

    Returns:
        Normalized store name string
    """
    if not name_str:
        return ""
    # Convert to uppercase and remove leading/trailing spaces
    return name_str.upper().strip()


def normalize_number(value_str: str) -> str:
    """
    Normalize numeric values by removing currency symbols and formatting.

    Args:
        value_str: Input numeric string

    Returns:
        Normalized number as string with two decimal places
    """
    try:
        # Handle empty or None values
        if not value_str:
            return ""

        # Extract digits and decimal point
        matches = re.search(r"([\d,.]+)", str(value_str))
        if not matches:
            return value_str

        number_str = matches.group(1)

        # Handle different number formats
        number_str = number_str.replace(",", ".")

        # Make sure we only have one decimal point
        parts = number_str.split(".")
        if len(parts) > 2:
            # Keep only the first decimal point
            number_str = parts[0] + "." + "".join(parts[1:]).replace(".", "")

        # Convert to float and format to 2 decimal places
        try:
            number = float(number_str)
            return f"{number:.2f}"
        except ValueError:
            return value_str
    except Exception as e:
        logger.error(f"Error normalizing number '{value_str}': {e}")
        return value_str


def post_process_prediction(raw_text: str) -> Dict[str, Any]:
    """
    Process raw model output to extract and normalize JSON data.

    Args:
        raw_text: Raw text output from the model

    Returns:
        Normalized JSON object
    """
    # Try to extract JSON from text
    data = extract_json_from_text(raw_text)

    if not data:
        return {"error": "Could not extract valid JSON"}

    # Normalize fields if they exist
    if "date_value" in data:
        data["date_value"] = normalize_date(data["date_value"])

    if "store_name_value" in data:
        data["store_name_value"] = normalize_store_name(data["store_name_value"])

    if "tax_value" in data:
        data["tax_value"] = normalize_number(data["tax_value"])

    if "total_value" in data:
        data["total_value"] = normalize_number(data["total_value"])

# Confidence scoring temporarily disabled for emergency restore

    return data


# All confidence scoring functions temporarily removed for emergency restore
