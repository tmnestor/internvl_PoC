#!/bin/bash
# Script to run evaluation on the SROIE dataset

# Get project root directory (one level up from scripts)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set up the environment
MODE="--local"  # Change to --remote if running on remote server

# Extract timestamp for output files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create necessary directories
mkdir -p "$PROJECT_ROOT/output/predictions_sroie"

# Print header and environment info
echo "=============================================================="
echo "SROIE Evaluation Pipeline"
echo "=============================================================="
echo ""
echo "Project root: $PROJECT_ROOT"
echo "Mode: $MODE (local/remote)"
echo ""

# Print current prompt setting from .env file
if grep -q "INTERNVL_PROMPT_NAME" "$PROJECT_ROOT/.env"; then
    PROMPT_NAME=$(grep "INTERNVL_PROMPT_NAME" "$PROJECT_ROOT/.env" | cut -d'=' -f2)
    echo "Using prompt from .env: $PROMPT_NAME"
else
    echo "WARNING: INTERNVL_PROMPT_NAME not found in .env file"
    echo "Using default prompt: default_receipt_prompt"
    PROMPT_NAME="default_receipt_prompt"
fi

echo ""
echo "First generate predictions on all SROIE images..."
cd "$PROJECT_ROOT" && bash ./scripts/run.sh $MODE predict \
  --test-image-dir "$PROJECT_ROOT/data/sroie/images" \
  --output-dir "$PROJECT_ROOT/output/predictions_sroie" \
  --prompt-name "$PROMPT_NAME"

# Check if prediction generation was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Prediction generation failed!"
    exit 1
fi

# Count prediction files
PREDICTION_COUNT=$(find "$PROJECT_ROOT/output/predictions_sroie" -name "*.json" | wc -l)
echo "Generated $PREDICTION_COUNT prediction files"

echo ""
echo "Now evaluating predictions against ground truth..."
cd "$PROJECT_ROOT" && bash ./scripts/run.sh $MODE evaluate \
  --predictions-dir "$PROJECT_ROOT/output/predictions_sroie" \
  --ground-truth-dir "$PROJECT_ROOT/data/sroie/ground_truth" \
  --output-path "$PROJECT_ROOT/output/evaluation_sroie_${TIMESTAMP}" \
  --show-examples

# Check if evaluation was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Evaluation failed!"
    exit 1
fi

echo ""
echo "=============================================================="
echo "Evaluation complete!"
echo "=============================================================="
echo ""
echo "Results saved to:"
echo "  - CSV: $PROJECT_ROOT/output/evaluation_sroie_${TIMESTAMP}.csv"
echo "  - JSON: $PROJECT_ROOT/output/evaluation_sroie_${TIMESTAMP}.json"
echo "  - Visualization: $PROJECT_ROOT/output/evaluation_sroie_${TIMESTAMP}.png"
echo ""