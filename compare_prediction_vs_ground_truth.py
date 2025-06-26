#!/usr/bin/env python3
"""
Compare a specific prediction against ground truth to see why F1-score is not 100%.
"""

import json
from pathlib import Path


def compare_sample():
    """Compare prediction vs ground truth for the test image."""
    
    # Check multiple possible prediction locations
    possible_pred_files = [
        "output/predictions_synthetic/sample_receipt_001.json",
        "output/predictions_test/sample_receipt_001.json", 
        "output/sample_receipt_001.json"
    ]
    
    pred_file = None
    for pf in possible_pred_files:
        if Path(pf).exists():
            pred_file = pf
            break
    
    if not pred_file:
        print("❌ Prediction file not found in any of these locations:")
        for pf in possible_pred_files:
            print(f"  {pf}")
        
        # Show what prediction files exist
        print("\nAvailable prediction files:")
        output_dir = Path("output")
        if output_dir.exists():
            for pred_dir in output_dir.glob("predictions*"):
                print(f"  {pred_dir}:")
                for json_file in pred_dir.glob("*.json")[:3]:
                    print(f"    {json_file.name}")
        return
    
    print(f"Found prediction file: {pred_file}")
    gt_file = "data/synthetic/ground_truth/sample_receipt_001.json"
    
    print("Checking if ground truth exists...")
    if not Path(gt_file).exists():
        print(f"❌ Ground truth file not found: {gt_file}")
        print("Available GT files:")
        gt_dir = Path("data/synthetic/ground_truth")
        if gt_dir.exists():
            for f in sorted(gt_dir.glob("*.json"))[:5]:
                print(f"  {f.name}")
        return
    
    # Load both files
    with Path(pred_file).open() as f:
        prediction = json.load(f)
    
    with Path(gt_file).open() as f:
        ground_truth = json.load(f)
    
    print("=" * 60)
    print("PREDICTION vs GROUND TRUTH COMPARISON")
    print("=" * 60)
    
    fields = ["date_value", "store_name_value", "tax_value", "total_value"]
    
    for field in fields:
        pred_val = prediction.get(field, "")
        gt_val = ground_truth.get(field, "")
        match = pred_val == gt_val
        status = "✅" if match else "❌"
        
        print(f"{field}:")
        print(f"  {status} Prediction: '{pred_val}'")
        print(f"     Ground Truth: '{gt_val}'")
        if not match:
            print("     → MISMATCH!")
        print()
    
    # Compare arrays
    array_fields = [
        ("prod_item_value", "Products"),
        ("prod_quantity_value", "Quantities"), 
        ("prod_price_value", "Prices")
    ]
    
    for field, name in array_fields:
        pred_arr = prediction.get(field, [])
        gt_arr = ground_truth.get(field, [])
        
        print(f"{name}:")
        print(f"  Prediction ({len(pred_arr)}): {pred_arr}")
        print(f"  Ground Truth ({len(gt_arr)}): {gt_arr}")
        
        if pred_arr == gt_arr:
            print("  ✅ EXACT MATCH")
        else:
            print("  ❌ MISMATCH!")
            # Show differences
            if len(pred_arr) != len(gt_arr):
                print(f"     → Length difference: {len(pred_arr)} vs {len(gt_arr)}")
            
            for i, (p, g) in enumerate(zip(pred_arr, gt_arr, strict=False)):
                if str(p) != str(g):
                    print(f"     → Item {i}: '{p}' vs '{g}'")
        print()
    
    print("=" * 60)
    print("This shows exactly why F1-score isn't 100%")

if __name__ == "__main__":
    compare_sample()