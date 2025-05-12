#!/usr/bin/env python3
"""
Create Project Structure

This module replaces the legacy create_project_structure.sh script with a Python equivalent.
It creates the directory and file structure for the InternVL Evaluation project.
"""

import argparse
import os
import sys
from pathlib import Path

from src.internvl.utils.logging import get_logger, setup_logging
from src.internvl.utils.path import enforce_module_invocation, project_root

# Enforce module invocation pattern
enforce_module_invocation("src.scripts")

logger = get_logger(__name__)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Create InternVL project structure")
    parser.add_argument(
        "--target-dir",
        type=str,
        default=".",
        help="Target directory for creating the project structure"
    )
    return parser.parse_args()


def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)
    return directory


def create_init_files(directory):
    """Create empty __init__.py files in all subdirectories."""
    for root, _, _ in os.walk(directory):
        init_file = os.path.join(root, "__init__.py")
        if not os.path.exists(init_file) and "/__pycache__" not in root:
            with open(init_file, "w") as f:
                pass  # Create empty file


def main():
    """Create the directory and file structure for the InternVL Evaluation project."""
    # Set up logging
    setup_logging()
    
    # Parse arguments
    args = parse_args()
    
    # Resolve target directory
    target_dir = Path(args.target_dir).absolute()
    logger.info(f"Creating project structure in: {target_dir}")
    
    # Create main project directories
    ensure_dir(target_dir / "data/generators")
    ensure_dir(target_dir / "data/sroie/ground_truth")
    ensure_dir(target_dir / "data/sroie/images")
    ensure_dir(target_dir / "data/synthetic/ground_truth")
    ensure_dir(target_dir / "data/synthetic/images")
    ensure_dir(target_dir / "docs")
    ensure_dir(target_dir / "output/evaluation_results")
    ensure_dir(target_dir / "output/predictions_test")
    
    # Create source directory structure
    src_root = target_dir / "src"
    ensure_dir(src_root)
    ensure_dir(src_root / "scripts")
    
    # Create internvl package structure
    internvl_root = src_root / "internvl"
    ensure_dir(internvl_root)
    
    # Create standard package structure
    for pkg in ["cli", "config", "evaluation", "extraction", "image", "model", "utils"]:
        ensure_dir(internvl_root / pkg)
    
    # Create __init__.py files
    create_init_files(src_root)
    
    # Create basic .env template file if it doesn't exist
    env_file = target_dir / ".env"
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("""# ==========================================================================
# InternVL Configuration Template - Australian Tax Office Version
# ==========================================================================
# This file is a template for the .env configuration file.
# Paths can be relative to the project root for KFP compatibility.

# Base paths (all relative to project root)
INTERNVL_PROJECT_ROOT=.
INTERNVL_DATA_PATH=data
INTERNVL_OUTPUT_PATH=output
INTERNVL_SOURCE_PATH=src
INTERNVL_PROMPTS_PATH=prompts.yaml

# Derived paths
INTERNVL_SYNTHETIC_DATA_PATH=${INTERNVL_DATA_PATH}/synthetic
INTERNVL_SROIE_DATA_PATH=${INTERNVL_DATA_PATH}/sroie
INTERNVL_IMAGE_FOLDER_PATH=${INTERNVL_SYNTHETIC_DATA_PATH}/images

# Path to the InternVL model (typically absolute)
INTERNVL_MODEL_PATH=/path/to/model

# Prompt name to use
INTERNVL_PROMPT_NAME=default_receipt_prompt
""")
            logger.info(f"Created template .env file: {env_file}")
    
    logger.info("Project structure creation complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())