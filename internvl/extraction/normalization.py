"""
Field normalization utilities for InternVL Evaluation

This module provides functions for normalizing field values extracted from model output.
"""

import os
import re
from typing import Any, Dict, Optional, Tuple

import dateparser

from internvl.extraction.json_extraction_fixed import extract_json_from_text
from internvl.utils import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Import confidence scoring if available
try:
    from .confidence import (
        calculate_confidence_score,
        get_confidence_summary,
        should_reprocess_prediction,
    )
    CONFIDENCE_AVAILABLE = True
except ImportError:
    logger.warning("Confidence scoring module not available")
    CONFIDENCE_AVAILABLE = False
    def calculate_confidence_score(_prediction):
        return 1.0, {}
    def should_reprocess_prediction(_confidence, _threshold):
        return False
    def get_confidence_summary(confidence, _components):
        return f"Confidence: {confidence:.2f}"


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


def post_process_prediction(raw_text: str, enable_confidence_scoring: Optional[bool] = None) -> Dict[str, Any]:
    """
    Process raw model output to extract and normalize JSON data.

    Args:
        raw_text: Raw text output from the model
        enable_confidence_scoring: Override for confidence scoring (None uses env var)

    Returns:
        Normalized JSON object with optional confidence metadata
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

    # Add confidence scoring if enabled
    if _is_confidence_scoring_enabled(enable_confidence_scoring):
        confidence, components = calculate_confidence_score(data)
        
        # Add confidence metadata (prefixed to avoid conflicts)
        data["_confidence_score"] = confidence
        data["_confidence_components"] = components
        data["_confidence_summary"] = get_confidence_summary(confidence, components)
        
        logger.info(f"Confidence scoring: {data['_confidence_summary']}")

    return data


def post_process_with_retry(
    raw_text: str, 
    image_path: str,
    retry_callback: Optional[callable] = None,
    enable_confidence_scoring: Optional[bool] = None
) -> Tuple[Dict[str, Any], bool]:
    """
    Process prediction with optional retry for low-confidence results.
    
    Args:
        raw_text: Raw text output from the model
        image_path: Path to the image (for retry)
        retry_callback: Function to call for retry (model, tokenizer, fallback_prompt) -> raw_text
        enable_confidence_scoring: Override for confidence scoring
        
    Returns:
        Tuple of (processed_prediction, was_retried)
    """
    # Initial processing
    data = post_process_prediction(raw_text, enable_confidence_scoring)
    
    if not _is_confidence_scoring_enabled(enable_confidence_scoring):
        return data, False
    
    # Check if retry is needed
    confidence = data.get("_confidence_score", 1.0)
    threshold = float(os.getenv("INTERNVL_CONFIDENCE_THRESHOLD", "0.7"))
    
    if should_reprocess_prediction(confidence, threshold) and retry_callback:
        logger.info(f"Low confidence ({confidence:.2f} < {threshold}), attempting retry...")
        
        try:
            # Get fallback prompt name
            fallback_prompt = os.getenv("INTERNVL_FALLBACK_PROMPT_NAME", "ultra_strict_json_prompt")
            
            # Attempt retry
            retry_raw_text = retry_callback(image_path, fallback_prompt)
            retry_data = post_process_prediction(retry_raw_text, enable_confidence_scoring)
            
            # Compare confidence scores
            retry_confidence = retry_data.get("_confidence_score", 0.0)
            
            if retry_confidence > confidence:
                logger.info(f"Retry improved confidence: {confidence:.2f} -> {retry_confidence:.2f}")
                retry_data["_retry_improved"] = True
                retry_data["_original_confidence"] = confidence
                return retry_data, True
            else:
                logger.info(f"Retry did not improve confidence: {retry_confidence:.2f} <= {confidence:.2f}")
                data["_retry_attempted"] = True
                data["_retry_confidence"] = retry_confidence
                
        except Exception as e:
            logger.error(f"Retry failed: {e}")
            data["_retry_failed"] = str(e)
    
    return data, False


def _is_confidence_scoring_enabled(override: Optional[bool] = None) -> bool:
    """Check if confidence scoring is enabled."""
    if override is not None:
        return override and CONFIDENCE_AVAILABLE
    
    env_enabled = os.getenv("INTERNVL_ENABLE_CONFIDENCE_SCORING", "false").lower()
    return env_enabled in ("true", "yes", "1", "y") and CONFIDENCE_AVAILABLE
