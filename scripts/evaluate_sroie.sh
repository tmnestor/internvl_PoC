#!/bin/bash
# Script to run evaluation on the SROIE dataset

# Get project root directory (one level up from scripts)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set up the environment
MODE="--local"  # Change to --remote if running on remote server

# Create necessary directories
mkdir -p "$PROJECT_ROOT/output/predictions_sroie"

# First generate predictions on all SROIE images
echo "Generating predictions on SROIE images..."
cd "$PROJECT_ROOT" && ./scripts/run.sh $MODE predict \
  --test-image-dir "$PROJECT_ROOT/raechel_gold_images" \
  --output-dir "$PROJECT_ROOT/output/predictions_sroie" \
  --image-pattern "sroie_test_*.jpg" \
  --prompt-name default_receipt_prompt

# Then evaluate the predictions against the ground truth
echo "Evaluating predictions against ground truth..."
cd "$PROJECT_ROOT" && ./scripts/run.sh $MODE evaluate \
  --predictions-dir "$PROJECT_ROOT/output/predictions_sroie" \
  --ground-truth-dir "$PROJECT_ROOT/raechel_gold_images/ground_truth"

echo "Evaluation complete! Results saved to output/evaluation_results.*"