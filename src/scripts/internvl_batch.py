#!/usr/bin/env python3
"""
InternVL Batch Image Information Extraction

This script processes multiple images in parallel with InternVL and extracts structured information.
"""

import argparse
import concurrent.futures as cf
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import torch

# Import from the src directory structure
# This is the correct import path when running as a module
from src.internvl.config import load_config, setup_argparse
from src.internvl.extraction.normalization import post_process_prediction
from src.internvl.image.loader import get_image_filepaths
from src.internvl.model import load_model_and_tokenizer
from src.internvl.model.inference import get_raw_prediction
from src.internvl.utils.logging import get_logger, setup_logging
from src.internvl.utils.path import path_manager


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = setup_argparse()
    parser.add_argument('--num-images', type=int,
                       help='Number of images to process (default: all)')
    parser.add_argument('--output-file', type=str,
                       help='Path to the output CSV file')
    parser.add_argument('--save-individual', action='store_true',
                       help='Save individual JSON files for each image')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    return parser.parse_args()

def process_image(
    image_path: str,
    model,
    tokenizer,
    prompt: str,
    generation_config: Dict[str, Any],
    device: str
) -> Dict[str, Any]:
    """Process a single image and return extracted information."""
    start_time = time.time()
    image_id = Path(image_path).stem
    
    try:
        # Get raw prediction
        raw_output = get_raw_prediction(
            image_path=image_path,
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            generation_config=generation_config,
            device=device
        )
        
        # Extract and normalize JSON
        processed_json = post_process_prediction(raw_output)
        
        # Add metadata
        result = {
            'image_id': image_id,
            'extracted_info': processed_json,
            'processing_time': time.time() - start_time
        }
        
        return result
    
    except Exception as e:
        return {
            'image_id': image_id,
            'error': str(e),
            'processing_time': time.time() - start_time
        }

def process_images_in_batch(
    image_paths: List[str],
    model,
    tokenizer,
    prompt: str,
    generation_config: Dict[str, Any],
    device: str,
    max_workers: int
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """Process multiple images in parallel."""
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                process_image,
                image_path=image_path,
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                generation_config=generation_config,
                device=device
            ): image_path for image_path in image_paths
        }
        
        # Process results as they complete
        for i, future in enumerate(cf.as_completed(futures), 1):
            try:
                result = future.result()
                results.append(result)
                
                # Log progress
                img_path = futures[future]
                print(f"Processed [{i}/{len(image_paths)}]: {Path(img_path).name}")
            except Exception as e:
                print(f"Error processing image: {e}")
    
    # Calculate statistics
    end_time = time.time()
    total_time = end_time - start_time
    processing_times = [r.get('processing_time', 0) for r in results]
    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    stats = {
        'total_time': total_time,
        'avg_processing_time': avg_time,
        'num_images': len(results),
        'num_errors': sum(1 for r in results if 'error' in r)
    }
    
    return results, stats

def main() -> int:
    """
    Main function for batch image processing.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Parse arguments
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = get_logger(__name__)
    
    try:
        # Load configuration
        config = load_config(args)
        
        # Get image folder path from config
        image_folder_path = Path(config['image_folder_path'])
        if not image_folder_path.exists():
            logger.error(f"Image folder not found: {image_folder_path}")
            return 1
        
        # Get image paths
        image_paths = get_image_filepaths(image_folder_path)
        if not image_paths:
            logger.error(f"No images found in {image_folder_path}")
            return 1
        
        # Limit number of images if specified
        if args.num_images is not None and args.num_images > 0:
            image_paths = image_paths[:args.num_images]
        
        logger.info(f"Processing {len(image_paths)} images with {config['max_workers']} workers")
        
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
        
        # Process images
        device = "cuda" if torch.cuda.is_available() else "cpu"
        generation_config = {
            "max_new_tokens": config.get("max_tokens", 1024),
            "do_sample": config.get("do_sample", False)
        }
        
        results, stats = process_images_in_batch(
            image_paths=image_paths,
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            generation_config=generation_config,
            device=device,
            max_workers=config.get("max_workers", 8)
        )
        
        # Save results
        if args.output_file:
            # Create DataFrame
            df_data = []
            for result in results:
                item = {'image_id': result['image_id']}
                if 'error' in result:
                    item['error'] = result['error']
                else:
                    for key, value in result['extracted_info'].items():
                        if isinstance(value, list):
                            item[key] = str(value)
                        else:
                            item[key] = value
                df_data.append(item)
            
            df = pd.DataFrame(df_data)
            df.to_csv(args.output_file, index=False)
            logger.info(f"Results saved to {args.output_file}")
        
        # Save individual JSON files if requested
        if args.save_individual:
            output_dir = path_manager.get_output_path("predictions")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for result in results:
                if 'error' not in result:
                    output_file = output_dir / f"{result['image_id']}.json"
                    with open(output_file, 'w') as f:
                        json.dump(result['extracted_info'], f, indent=2)
            
            logger.info(f"Individual JSON files saved to {output_dir}")
        
        # Print statistics
        print("\nProcessing Statistics:")
        print(f"Total time: {stats['total_time']:.2f}s")
        print(f"Average time per image: {stats['avg_processing_time']:.2f}s")
        print(f"Images processed: {stats['num_images']}")
        print(f"Errors: {stats['num_errors']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())