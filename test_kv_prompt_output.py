#!/usr/bin/env python3
"""
Test what format the model actually outputs with the key-value prompt.
"""

import yaml
from pathlib import Path
from internvl.config import load_config
from internvl.image.loader import get_image_filepaths
from internvl.model import load_model_and_tokenizer
from internvl.model.inference import get_raw_prediction
import torch

def test_model_output():
    """Test a single image to see what format the model generates."""
    
    # Load config and get first test image
    config = load_config()
    images = get_image_filepaths(Path("data/synthetic/images"))
    
    if not images:
        print("❌ No test images found")
        return
    
    test_image = images[0]
    print(f"Testing with: {test_image}")
    
    # Load the key-value prompt
    prompts_path = config.get("prompts_path", "prompts.yaml")
    with Path(prompts_path).open('r') as f:
        prompts = yaml.safe_load(f)
    
    prompt_name = config.get("prompt_name")
    prompt = prompts.get(prompt_name)
    
    print(f"Using prompt: {prompt_name}")
    print(f"Prompt preview: {prompt[:200]}...")
    
    # Load model 
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, tokenizer = load_model_and_tokenizer(config["model_path"], device)
    
    # Generate prediction
    generation_config = {
        "max_new_tokens": config.get("max_tokens", 1024),
        "do_sample": config.get("do_sample", False),
    }
    
    print("\nGenerating model output...")
    raw_output = get_raw_prediction(
        image_path=test_image,
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        generation_config=generation_config,
        device=device,
    )
    
    print("=" * 60)
    print("RAW MODEL OUTPUT:")
    print("=" * 60)
    print(raw_output)
    print("=" * 60)
    
    # Check what format it actually is
    if "DATE:" in raw_output and "STORE:" in raw_output:
        print("✅ Model is outputting KEY-VALUE format!")
    elif "{" in raw_output and "date_value" in raw_output:
        print("❌ Model is still outputting JSON format!")
    else:
        print("❓ Model output format is unclear")
    
    # Test the extraction
    from internvl.extraction import extract_structured_data
    extracted = extract_structured_data(raw_output)
    
    print("\nExtracted data:")
    print(f"Date: {extracted.get('date_value')}")
    print(f"Store: {extracted.get('store_name_value')}")
    print(f"Products: {extracted.get('prod_item_value', [])}")
    print(f"Product count: {len(extracted.get('prod_item_value', []))}")

if __name__ == "__main__":
    test_model_output()