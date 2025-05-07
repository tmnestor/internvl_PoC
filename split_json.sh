#!/bin/bash
# Script to split nested JSON into individual files

# Get the input file
INPUT_FILE="raechel_gold_images/ground_truth_sroie_v5.json"
OUTPUT_DIR="raechel_gold_images/ground_truth"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Get the number of entries in the JSON file
NUM_ENTRIES=$(jq 'length' "$INPUT_FILE")
echo "Found $NUM_ENTRIES entries in $INPUT_FILE"

# Extract each entry and save to a separate file
for i in $(seq 0 $((NUM_ENTRIES-1))); do
  # Format number with leading zeros
  padded_i=$(printf "%03d" $i)
  
  # Extract the JSON for this entry
  jq -r ".[\"$i\"]" "$INPUT_FILE" > "$OUTPUT_DIR/sroie_test_${padded_i}.json"
  
  # Print a message
  echo "Created $OUTPUT_DIR/sroie_test_${padded_i}.json"
done

echo "Done! All JSON files have been created in $OUTPUT_DIR"