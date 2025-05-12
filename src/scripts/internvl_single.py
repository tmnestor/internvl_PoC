#!/usr/bin/env python3
"""
InternVL Single Image Information Extraction

This script processes a single image with InternVL and extracts structured information.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import torch

# Import from the src directory structure
# This is the correct import path when running as a module
from src.internvl.config import load_config, setup_argparse
from src.internvl.extraction.normalization import post_process_prediction
from src.internvl.model import load_model_and_tokenizer
from src.internvl.model.inference import get_raw_prediction
from src.internvl.utils.logging import get_logger, setup_logging


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = setup_argparse()
    parser.add_argument('--image-path', type=str, required=True,
                       help='Path to the image file to process')
    parser.add_argument('--output-file', type=str,
                       help='Path to the output JSON file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    return parser.parse_args()

def main() -> int:
    """
    Main function for single image processing.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse arguments
        args = parse_args()

        # Setup logging
        log_level = logging.DEBUG if args.verbose else logging.INFO

        # Load configuration to get transformers log level
        config = load_config(args)
        transformers_log_level = config.get("transformers_log_level", "WARNING")

        setup_logging(log_level, transformers_log_level=transformers_log_level)
    except SystemExit:
        print("Error: Missing required argument --image-path")
        print("Usage: python -m src.scripts.internvl_single --image-path /path/to/image.jpg")
        return 1
    logger = get_logger(__name__)

    # Resolve image path - use a clear, explicit approach
    image_path = args.image_path
    image_path_obj = Path(image_path)

    # If path is not absolute and doesn't exist, try using project root only
    if not image_path_obj.is_absolute() and not image_path_obj.exists():
        # Try relative to project root only - the most common case for KFP
        from src.internvl.utils.path import resolve_path
        project_root = Path(os.environ.get("INTERNVL_PROJECT_ROOT", ".")).absolute()
        alt_path = project_root / image_path_obj

        # Only update if the file exists at new path
        if alt_path.exists():
            image_path = str(alt_path)
            logger.info(f"Resolved relative path to project root: {image_path}")

    # Update the argument with the resolved path
    args.image_path = image_path

    # Verify file exists before proceeding
    if not Path(args.image_path).exists():
        raise FileNotFoundError(f"Image file not found: {args.image_path}")

    logger.info(f"Processing image: {args.image_path}")
    
    try:
        # Load configuration
        config = load_config(args)
        
        # Get the prompt
        try:
            import yaml
            prompts_path = config.get("prompts_path")
            prompt_name = config.get("prompt_name")
            
            if prompts_path and Path(prompts_path).exists():
                with open(prompts_path, 'r') as f:
                    prompts = yaml.safe_load(f)
                prompt = prompts.get(prompt_name, "")
                logger.info(f"Using prompt '{prompt_name}' from {prompts_path}")
            else:
                prompt = "<image>\nExtract information from this receipt and return it in JSON format."
                logger.warning("Prompts file not found, using default prompt")
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            prompt = "<image>\nExtract information from this receipt and return it in JSON format."
        
        # Load model and tokenizer
        model, tokenizer = load_model_and_tokenizer(
            model_path=config['model_path'],
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
        # Process image
        try:
            raw_output = get_raw_prediction(
                image_path=args.image_path,
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                generation_config={
                    "max_new_tokens": config.get("max_tokens", 1024),
                    "do_sample": config.get("do_sample", False)
                },
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            # Extract JSON and normalize
            processed_json = post_process_prediction(raw_output)
            
            # Save result
            output_file = args.output_file
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(processed_json, f, indent=2)
                logger.info(f"Result saved to {output_file}")
            else:
                # Print result to stdout
                print(json.dumps(processed_json, indent=2))
            
            return 0
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return 1
    
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())