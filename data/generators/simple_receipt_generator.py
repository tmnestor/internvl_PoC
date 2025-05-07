#!/usr/bin/env python
"""
Simple Australian receipt generator that creates receipts for testing only.
Since we're not performing fine-tuning, we only generate test data.
"""
import argparse
import json
import os
import random
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont


def generate_receipt(output_dir, ground_truth_dir, include_gst=True, receipt_id=None):
    """Generate a single synthetic Australian receipt"""
    if receipt_id is None:
        receipt_id = f"sample_receipt_{random.randint(1, 999):03d}"
    
    # Create a blank white receipt
    width, height = 600, 1200
    receipt = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(receipt)
    
    # Try to load a font or use default
    try:
        header_font = ImageFont.truetype("Arial", 30)
        normal_font = ImageFont.truetype("Arial", 20)
    except IOError:
        print("Arial font not found, using default...")
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # Store ground truth data
    ground_truth = {}
    
    # Draw header (store name)
    store_choices = ["WOOLWORTHS", "COLES", "ALDI", "IGA", "KMART", "BIG W", "TARGET"]
    store_name = random.choice(store_choices)
    draw.text((width//2, 40), store_name, fill='black', font=header_font, anchor="mt")
    ground_truth["store_name"] = store_name
    
    # Draw date
    today = datetime.now()
    days_ago = random.randint(0, 30)
    receipt_date = today - timedelta(days=days_ago)
    date_str = receipt_date.strftime("%d/%m/%Y")
    draw.text((30, 100), f"Date: {date_str}", fill='black', font=normal_font)
    ground_truth["date"] = date_str
    
    # Draw items
    items = [
        "Milk 2L", "Bread", "Eggs 12pk", "Bananas 1kg", 
        "Coffee 200g", "Chocolate", "Chicken Breast", "Rice 1kg"
    ]
    selected_items = random.sample(items, k=min(5, len(items)))
    
    # Initialize lists for ground truth
    ground_truth["items"] = []
    ground_truth["quantities"] = []
    ground_truth["prices"] = []
    
    y_pos = 180
    subtotal = 0
    
    # Draw items, quantities and prices
    for item in selected_items:
        qty = random.randint(1, 3)
        price = round(random.uniform(2.50, 25.00), 2)
        total_price = qty * price
        subtotal += total_price
        
        draw.text((30, y_pos), f"{item}", fill='black', font=normal_font)
        draw.text((400, y_pos), f"{qty}", fill='black', font=normal_font)
        draw.text((500, y_pos), f"${price:.2f}", fill='black', font=normal_font)
        
        # Add to ground truth
        ground_truth["items"].append(item)
        ground_truth["quantities"].append(str(qty))
        ground_truth["prices"].append(f"{price:.2f}")
        
        y_pos += 40
    
    # Draw subtotal
    y_pos += 20
    draw.text((30, y_pos), "Subtotal:", fill='black', font=normal_font)
    draw.text((500, y_pos), f"${subtotal:.2f}", fill='black', font=normal_font)
    
    # Draw GST (10% in Australia)
    if include_gst:
        y_pos += 40
        gst = round(subtotal / 11, 2)  # GST is 1/11 of the total in Australia
        draw.text((30, y_pos), "GST (10%):", fill='black', font=normal_font)
        draw.text((500, y_pos), f"${gst:.2f}", fill='black', font=normal_font)
        ground_truth["tax"] = f"{gst:.2f}"
    else:
        ground_truth["tax"] = "0.00"
    
    # Draw total
    y_pos += 40
    draw.text((30, y_pos), "Total:", fill='black', font=normal_font, weight="bold")
    draw.text((500, y_pos), f"${subtotal:.2f}", fill='black', font=normal_font, weight="bold")
    ground_truth["total"] = f"{subtotal:.2f}"
    
    # Save receipt image
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"{receipt_id}.jpg")
    receipt.save(image_path)
    print(f"Created receipt: {image_path}")
    
    # Save ground truth for information extraction
    if ground_truth_dir:
        os.makedirs(ground_truth_dir, exist_ok=True)
        ground_truth_path = os.path.join(ground_truth_dir, f"{receipt_id}.json")
        with open(ground_truth_path, 'w') as f:
            json.dump(ground_truth, f, indent=2)
        print(f"Created ground truth file: {ground_truth_path}")
    
    return image_path, ground_truth

def setup_test_directories(base_dir):
    """Create only the test directory structure, no train/val since we're not fine-tuning"""
    # Create test directories
    test_img_dir = os.path.join(base_dir, "test", "images") 
    test_ground_truth_dir = os.path.join(base_dir, "test", "ground_truth")
    
    # Ensure directories exist
    os.makedirs(test_img_dir, exist_ok=True)
    os.makedirs(test_ground_truth_dir, exist_ok=True)
    
    return {
        "test_img_dir": test_img_dir,
        "test_ground_truth_dir": test_ground_truth_dir
    }

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Australian receipts for testing only")
    parser.add_argument("--base_dir", type=str, default="data/synthetic", 
                        help="Base directory for synthetic data (default: data/synthetic)")
    parser.add_argument("--num_receipts", type=int, default=20, 
                        help="Number of test receipts to generate (default: 20)")
    parser.add_argument("--include_gst", action="store_true", help="Include GST (Australian tax)")
    args = parser.parse_args()
    
    # Convert to absolute path if relative path provided
    base_dir = os.path.abspath(args.base_dir)
    print(f"Using base directory: {base_dir}")
    
    # Setup directory structure (only test, no train/val)
    dirs = setup_test_directories(base_dir)
    
    print(f"Generating {args.num_receipts} Australian receipts for testing with GST: {args.include_gst}")
    
    # Generate test receipts
    for i in range(args.num_receipts):
        receipt_id = f"sample_receipt_{i+1:03d}"
        generate_receipt(
            dirs["test_img_dir"], 
            dirs["test_ground_truth_dir"], 
            include_gst=args.include_gst,
            receipt_id=receipt_id
        )
    
    print(f"Successfully generated {args.num_receipts} test receipts")
    print(f"\nTest directory structure created at {base_dir}:")
    print(f"- Images: {dirs['test_img_dir']}")
    print(f"- Ground truth: {dirs['test_ground_truth_dir']}")

if __name__ == "__main__":
    main()