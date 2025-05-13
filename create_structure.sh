#!/bin/bash

# Script to recreate the internvl_PoC project structure
# Created by Claude

# Create main directories
mkdir -p data/generators
mkdir -p data/sroie/ground_truth
mkdir -p data/sroie/images
mkdir -p data/synthetic/ground_truth
mkdir -p data/synthetic/images
mkdir -p data/synthetic/test
mkdir -p docs
mkdir -p output/predictions_sroie
mkdir -p output/predictions_test
mkdir -p src/internvl/cli
mkdir -p src/internvl/config
mkdir -p src/internvl/evaluation
mkdir -p src/internvl/extraction
mkdir -p src/internvl/image
mkdir -p src/internvl/model
mkdir -p src/internvl/utils
mkdir -p src/scripts/utils

# Create placeholder files for Python modules
touch README.md
touch data/generators/README.md
touch data/generators/receipt_generator.py
touch data/generators/simple_receipt_generator.py
touch docs/KFP_COMPATIBILITY.md
touch docs/SHARED_ENVIRONMENTS.md
touch internvl_env.yml
touch prompts.yaml
touch src/__init__.py
touch src/internvl/__init__.py
touch src/internvl/cli/__init__.py
touch src/internvl/config/__init__.py
touch src/internvl/config/config.py
touch src/internvl/evaluation/__init__.py
touch src/internvl/evaluation/metrics.py
touch src/internvl/extraction/__init__.py
touch src/internvl/extraction/json_extraction.py
touch src/internvl/extraction/normalization.py
touch src/internvl/image/__init__.py
touch src/internvl/image/loader.py
touch src/internvl/image/preprocessing.py
touch src/internvl/model/__init__.py
touch src/internvl/model/inference.py
touch src/internvl/model/loader.py
touch src/internvl/utils/__init__.py
touch src/internvl/utils/logging.py
touch src/internvl/utils/path.py
touch src/scripts/__init__.py
touch src/scripts/create_project_structure.py
touch src/scripts/evaluate_extraction.py
touch src/scripts/evaluate_sroie.py
touch src/scripts/generate_predictions.py
touch src/scripts/internvl_batch.py
touch src/scripts/internvl_single.py
touch src/scripts/module_template.py
touch src/scripts/split_json.py
touch src/scripts/test_image_resolution.py
touch src/scripts/test_image_resolution_fail.py
touch src/scripts/test_path_resolution.py
touch src/scripts/utils/__init__.py
touch src/scripts/utils/verify_env.py
touch test_receipt.png

# Create placeholders for ground truth files
for n in 000 001 003 004 007 008 009 010 011 012 013 014 015 016 017 018 019 020 021 022 024 025 026 027 028 029 031 032 033
do
  touch "data/sroie/ground_truth/sroie_test_$n.json"
  touch "data/sroie/images/sroie_test_$n.jpg"
done

# Create ground truth combined file
touch data/sroie/ground_truth_sroie_v5.json

# Create synthetic data placeholders
for i in $(seq -f "%03g" 1 30)
do
  touch "data/synthetic/ground_truth/sample_receipt_$i.json"
  touch "data/synthetic/images/sample_receipt_$i.jpg"
done

echo "Project structure created successfully!"