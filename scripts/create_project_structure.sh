#!/bin/bash
# Script to recreate the directory and file structure of the internvl_PoC project
# This is useful for migrating to an environment without internet access

# Get the script directory and calculate project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set target directory (defaults to current directory if not provided)
TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "Creating project structure in: $TARGET_DIR"

# Create main project directories
mkdir -p "$TARGET_DIR"/data/generators
mkdir -p "$TARGET_DIR"/data/sroie/ground_truth/
mkdir -p "$TARGET_DIR"/data/sroie/images/
mkdir -p "$TARGET_DIR"/data/synthetic/ground_truth/
mkdir -p "$TARGET_DIR"/data/synthetic/images/
mkdir -p "$TARGET_DIR"/docs
mkdir -p "$TARGET_DIR"/output/evaluation_results
mkdir -p "$TARGET_DIR"/output/predictions_test
mkdir -p "$TARGET_DIR"/scripts
mkdir -p "$TARGET_DIR"/src/internvl/{cli,config,evaluation,extraction,image,model,utils}/__init__
mkdir -p "$TARGET_DIR"/src/scripts/__init__

# Create empty files for Python modules
find "$TARGET_DIR"/src -type d -name "__init__" -exec touch {}/__init__.py \;

# Copy or create key files
# Configuration files
cp "$PROJECT_ROOT"/internvl_env.yml "$TARGET_DIR"/
cp "$PROJECT_ROOT"/internvl_env_artifactory.yml "$TARGET_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/prompts.yaml "$TARGET_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/.env "$TARGET_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/.env.example "$TARGET_DIR"/ 2>/dev/null || true

# Documentation files
cp "$PROJECT_ROOT"/README.md "$TARGET_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/MIGRATION.md "$TARGET_DIR"/ 2>/dev/null || true
cp "$PROJECT_ROOT"/docs/* "$TARGET_DIR"/docs/ 2>/dev/null || true

# Scripts
cp "$PROJECT_ROOT"/scripts/*.sh "$TARGET_DIR"/scripts/ 2>/dev/null || true
cp "$PROJECT_ROOT"/scripts/*.py "$TARGET_DIR"/scripts/ 2>/dev/null || true

# Source files
cp -r "$PROJECT_ROOT"/src/internvl/* "$TARGET_DIR"/src/internvl/ 2>/dev/null || true
cp -r "$PROJECT_ROOT"/src/scripts/* "$TARGET_DIR"/src/scripts/ 2>/dev/null || true

# Create a file with the directory structure for reference
find "$TARGET_DIR" -type d | sort > "$TARGET_DIR"/directory_structure.txt
find "$TARGET_DIR" -type f -name "*.py" | sort > "$TARGET_DIR"/python_files.txt
find "$TARGET_DIR" -type f -name "*.sh" | sort > "$TARGET_DIR"/shell_scripts.txt
find "$TARGET_DIR" -type f -name "*.md" | sort > "$TARGET_DIR"/markdown_docs.txt

echo "Project structure created successfully in: $TARGET_DIR"
echo "See directory_structure.txt for the complete directory listing"

# Create a README specifically for the offline environment
cat > "$TARGET_DIR"/OFFLINE_SETUP.md << 'EOF'
# InternVL Offline Setup Guide

This directory contains the file and directory structure for the InternVL project, ready for offline use.

## Directory Structure

The main directories are:
- `data/`: Contains the SROIE and synthetic datasets
- `docs/`: Project documentation
- `output/`: Directory for prediction outputs and evaluation results
- `scripts/`: Shell scripts and utility Python scripts
- `src/`: Source code for the InternVL package

## Setting Up in an Offline Environment

1. **Transfer the files**:
   - Copy this entire directory structure to your offline environment
   - Ensure all file permissions are preserved (use `tar` with the `-p` option)

2. **Set up the conda environment**:
   ```bash
   # If your offline environment has conda with access to an internal repository:
   conda env create -f internvl_env.yml -p /path/to/shared/internvl_env
   
   # If using an internal artifactory:
   conda env create -f internvl_env_artifactory.yml -p /path/to/shared/internvl_env
   
   # If using Python venv instead:
   ./scripts/setup_venv.sh /path/to/venv
   ```

3. **Configure environment variables**:
   ```bash
   # Copy the example .env file
   cp .env.example .env
   
   # Edit the .env file with your offline paths
   nano .env
   ```

4. **Model files**:
   - You'll need to ensure the InternVL model files are available in your offline environment
   - Update the `INTERNVL_MODEL_PATH` in your .env file to point to the model location

5. **Verify your setup**:
   ```bash
   # Run the environment verification
   python scripts/verify_env.py
   
   # Test with a single image (if sample images are available)
   ./scripts/run.sh single --image-path /path/to/test_receipt.png
   ```

## Managing the Environment Offline

- See `docs/SHARED_ENVIRONMENTS.md` for managing shared environments
- If package updates are needed, prepare them on an online machine and transfer the updated environment files

EOF

echo "Created OFFLINE_SETUP.md with instructions for offline setup"

# Mark scripts as executable
find "$TARGET_DIR"/scripts -name "*.sh" -exec chmod +x {} \;
find "$TARGET_DIR"/scripts -name "*.py" -exec chmod +x {} \;

echo "Done!"