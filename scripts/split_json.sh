#!/bin/bash
# Script to split nested JSON into individual files

# Get the input file with absolute path
# Get project root directory (one level up from scripts)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Use absolute paths with PROJECT_ROOT
INPUT_FILE="$PROJECT_ROOT/data/sroie/ground_truth_sroie_v5.json"
OUTPUT_DIR="$PROJECT_ROOT/data/sroie/ground_truth"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Get the image files to match against
IMAGE_FILES=($(ls -1 "$PROJECT_ROOT/data/sroie/images/sroie_test_*.jpg" | sort))
echo "Found ${#IMAGE_FILES[@]} image files in $PROJECT_ROOT/data/sroie/images/"

# Extract each entry and save to a file matching the image filename pattern
for image_path in "${IMAGE_FILES[@]}"; do
  # Extract the image filename without path or extension
  image_file=$(basename "$image_path")
  image_name="${image_file%.*}"
  
  # Extract image index from filename (e.g., "sroie_test_033" -> "33")
  image_index=$(echo "$image_name" | sed -E 's/sroie_test_0*([0-9]+)/\1/')
  
  # Extract the JSON for this entry using the actual image index
  jq -r ".[\"$image_index\"]" "$INPUT_FILE" > "$OUTPUT_DIR/${image_name}.json"
  
  # Print a message
  echo "Created $OUTPUT_DIR/${image_name}.json from JSON index $image_index"
done

echo "Done! All JSON files have been created in $OUTPUT_DIR matching image filenames"