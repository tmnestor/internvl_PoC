#!/bin/bash
# Script to run evaluation on the SROIE dataset

# Set up the environment
MODE="--local"  # Change to --remote if running on remote server

# Create necessary directories
mkdir -p output/predictions_sroie

# First generate predictions on all SROIE images
echo "Generating predictions on SROIE images..."
./run.sh $MODE predict \
  --test-image-dir $(pwd)/raechel_gold_images \
  --output-dir $(pwd)/output/predictions_sroie \
  --image-pattern "sroie_test_*.jpg" \
  --prompt-name default_receipt_prompt

# Then evaluate the predictions against the ground truth
echo "Evaluating predictions against ground truth..."
./run.sh $MODE evaluate \
  --predictions-dir $(pwd)/output/predictions_sroie \
  --ground-truth-dir $(pwd)/raechel_gold_images/ground_truth

echo "Evaluation complete! Results saved to output/evaluation_results.*"