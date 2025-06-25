"""
Extraction module for InternVL Evaluation

This module handles JSON extraction and normalization.
"""

from .json_extraction import extract_json_from_response, extract_json_from_text
from .normalization import (
    normalize_date,
    normalize_number,
    normalize_store_name,
    post_process_prediction,
)

__all__ = [
    "extract_json_from_text",
    "extract_json_from_response",
    "normalize_date",
    "normalize_store_name",
    "normalize_number",
    "post_process_prediction",
]
