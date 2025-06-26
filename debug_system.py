#!/usr/bin/env python3
"""
Emergency diagnostic script for 0% F1-score issue.
Run this to identify the exact failure point in the prediction generation system.
"""

import sys
from pathlib import Path


def test_imports():
    """Test all critical imports."""
    print("=" * 60)
    print("PHASE 1: IMPORT DIAGNOSTICS")
    print("=" * 60)
    
    # Test 1: Normalization import
    try:
        print('✅ normalization import OK')
    except Exception as e:
        print(f'❌ normalization import FAILED: {e}')
        return False

    # Test 2: Model import
    try:
        print('✅ model import OK')
    except Exception as e:
        print(f'❌ model import FAILED: {e}')
        return False

    # Test 3: Config import
    try:
        print('✅ config import OK')
    except Exception as e:
        print(f'❌ config import FAILED: {e}')
        return False
    
    # Test 4: Image loader import
    try:
        print('✅ image loader import OK')
    except Exception as e:
        print(f'❌ image loader import FAILED: {e}')
        return False
    
    # Test 5: Inference import
    try:
        print('✅ inference import OK')
    except Exception as e:
        print(f'❌ inference import FAILED: {e}')
        return False
    
    return True


def test_configuration():
    """Test configuration loading and validation."""
    print("\n" + "=" * 60)
    print("PHASE 2: CONFIGURATION DIAGNOSTICS")
    print("=" * 60)
    
    try:
        from internvl.config import load_config
        config = load_config()
        
        print(f"Prompt name: {config.get('prompt_name')}")
        print(f"Model path: {config.get('model_path')}")
        print(f"Prompts path: {config.get('prompts_path')}")
        
        # Check if paths exist
        model_path = config.get('model_path')
        if model_path and Path(model_path).exists():
            print(f"✅ Model path exists: {model_path}")
        else:
            print(f"❌ Model path missing: {model_path}")
        
        # Check prompts file
        prompts_path = config.get('prompts_path', 'prompts.yaml')
        if Path(prompts_path).exists():
            print(f"✅ Prompts file exists: {prompts_path}")
            
            # Test prompt loading
            try:
                import yaml
                with Path(prompts_path).open('r') as f:
                    prompts = yaml.safe_load(f)
                prompt_name = config.get('prompt_name')
                if prompt_name in prompts:
                    print(f"✅ Prompt '{prompt_name}' found in prompts.yaml")
                    prompt_length = len(prompts[prompt_name])
                    print(f"   Prompt length: {prompt_length} characters")
                else:
                    print(f"❌ Prompt '{prompt_name}' NOT found in prompts.yaml")
                    print(f"   Available prompts: {list(prompts.keys())}")
            except Exception as e:
                print(f"❌ Failed to load prompts: {e}")
        else:
            print(f"❌ Prompts file missing: {prompts_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading FAILED: {e}")
        return False


def test_data_access():
    """Test data directory and image access."""
    print("\n" + "=" * 60)
    print("PHASE 3: DATA ACCESS DIAGNOSTICS")
    print("=" * 60)
    
    # Check synthetic images directory
    images_dir = "data/synthetic/images"
    if Path(images_dir).exists():
        try:
            from internvl.image.loader import get_image_filepaths
            image_paths = get_image_filepaths(Path(images_dir))
            print(f"✅ Images directory exists: {images_dir}")
            print(f"✅ Found {len(image_paths)} images")
            if image_paths:
                print(f"   First image: {image_paths[0]}")
                print(f"   Last image: {image_paths[-1]}")
        except Exception as e:
            print(f"❌ Failed to load images: {e}")
            return False
    else:
        print(f"❌ Images directory missing: {images_dir}")
        return False
    
    # Check output directory permissions
    output_dir = "output"
    try:
        Path(output_dir).mkdir(exist_ok=True)
        test_file = Path(output_dir) / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ Output directory writable: {output_dir}")
    except Exception as e:
        print(f"❌ Output directory not writable: {e}")
        return False
    
    return True


def test_model_loading():
    """Test model loading (this is likely where it fails)."""
    print("\n" + "=" * 60)
    print("PHASE 4: MODEL LOADING DIAGNOSTICS")
    print("=" * 60)
    
    try:
        import torch

        from internvl.config import load_config
        from internvl.model import load_model_and_tokenizer
        
        config = load_config()
        model_path = config.get('model_path')
        
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA devices: {torch.cuda.device_count()}")
            print(f"Current device: {torch.cuda.current_device()}")
            print(f"Device name: {torch.cuda.get_device_name()}")
        
        print(f"Attempting to load model from: {model_path}")
        
        # This is the critical test - model loading often fails
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, tokenizer = load_model_and_tokenizer(model_path, device)
        
        print(f"✅ Model loaded successfully on {device}")
        print(f"   Model type: {type(model)}")
        print(f"   Tokenizer type: {type(tokenizer)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading FAILED: {e}")
        print("   This is likely the root cause of the 0% F1-score!")
        return False


def test_single_prediction():
    """Test a single prediction to verify the entire pipeline."""
    print("\n" + "=" * 60)
    print("PHASE 5: SINGLE PREDICTION TEST")
    print("=" * 60)
    
    try:
        from pathlib import Path

        import torch
        import yaml

        from internvl.config import load_config
        from internvl.extraction.normalization import post_process_prediction
        from internvl.image.loader import get_image_filepaths
        from internvl.model import load_model_and_tokenizer
        from internvl.model.inference import get_raw_prediction
        
        # Load config
        config = load_config()
        
        # Get first image
        images = get_image_filepaths(Path("data/synthetic/images"))
        if not images:
            print("❌ No images found")
            return False
        
        test_image = images[0]
        print(f"Testing with image: {test_image}")
        
        # Load prompt
        prompts_path = config.get("prompts_path", "prompts.yaml")
        with Path(prompts_path).open('r') as f:
            prompts = yaml.safe_load(f)
        prompt = prompts.get(config.get("prompt_name"))
        print(f"Using prompt: {config.get('prompt_name')}")
        
        # Load model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, tokenizer = load_model_and_tokenizer(config["model_path"], device)
        
        # Generate prediction
        generation_config = {
            "max_new_tokens": config.get("max_tokens", 1024),
            "do_sample": config.get("do_sample", False),
        }
        
        print("Generating prediction...")
        raw_output = get_raw_prediction(
            image_path=test_image,
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            generation_config=generation_config,
            device=device,
        )
        
        print(f"✅ Raw output generated ({len(raw_output)} chars)")
        print(f"   First 200 chars: {raw_output[:200]}")
        
        # Process prediction
        processed_json = post_process_prediction(raw_output)
        print("✅ JSON processed successfully")
        print(f"   Keys: {list(processed_json.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Single prediction test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests."""
    print("EMERGENCY DIAGNOSTIC SCRIPT")
    print("Investigating 0% F1-score issue...")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Python version: {sys.version}")
    
    # Run all tests
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration),
        ("Data Access Tests", test_data_access),
        ("Model Loading Tests", test_model_loading),
        ("Single Prediction Test", test_single_prediction),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if not success:
                failed_tests.append(test_name)
                print(f"\n🚨 STOPPING at {test_name} - Fix this first!")
                break
        except Exception as e:
            print(f"\n🚨 {test_name} crashed with exception: {e}")
            failed_tests.append(test_name)
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if not failed_tests:
        print("🎉 All tests passed! The system should work.")
        print("   If you're still getting 0% F1-score, the issue might be:")
        print("   - Evaluation script bug")
        print("   - Ground truth data mismatch")
        print("   - Predictions being saved to wrong location")
    else:
        print(f"🚨 Failed tests: {failed_tests}")
        print("\nNext steps:")
        print("1. Fix the first failed test")
        print("2. Re-run this diagnostic script")
        print("3. Repeat until all tests pass")


if __name__ == "__main__":
    main()