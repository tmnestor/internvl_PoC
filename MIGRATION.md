# Migration to Python Package Structure

This document summarizes the migration of InternVL from Jupyter notebooks to a proper Python package structure.

## Migration Summary

The InternVL project was successfully migrated from:
- A collection of Jupyter notebooks (.ipynb files)
- Standalone utility scripts
- No formal package structure

To:
- A proper Python package with `src/internvl` namespace
- Modular organization with clear separation of concerns
- Command-line interface for all operations
- Unified configuration and path management

## Key Improvements

1. **Proper Module Structure**
   - Organized code into logical modules (model, image, extraction, evaluation)
   - Implemented proper imports with consistent namespace (src.internvl.*)
   - Eliminated circular dependencies between modules

2. **Environment and Configuration**
   - Centralized environment variables in `.env` file
   - Implemented robust configuration validation
   - Created PathManager for consistent path handling across modules

3. **Command Line Interface**
   - Added command-line scripts for all operations
   - Created a convenience `run.sh` script for easier execution
   - Added proper argument parsing and help documentation

4. **Prompt Management**
   - Centralized prompt templates in `prompts.yaml`
   - Flexible prompt selection via configuration
   - Added specialized prompts for different use cases

5. **Code Quality**
   - Added type hints for better IDE support
   - Improved error handling and logging
   - Enhanced documentation with docstrings and README files

## Structure Overview

- `src/internvl/`: Core package modules
  - `config/`: Configuration management
  - `evaluation/`: Evaluation metrics and reporting
  - `extraction/`: JSON extraction and normalization
  - `image/`: Image processing and tiling
  - `model/`: Model loading and inference
  - `utils/`: Shared utilities (logging, path management)

- `src/scripts/`: Command-line entry points
  - `internvl_single.py`: Process a single image
  - `internvl_batch.py`: Process multiple images
  - `generate_predictions.py`: Generate predictions on test data
  - `evaluate_extraction.py`: Evaluate extraction results

## Usage

The migrated code can be used in two ways:

1. **Via run.sh helper script**:
   ```bash
   ./run.sh single --image-path /path/to/image.jpg
   ```

2. **Direct Python module execution**:
   ```bash
   python -m src.scripts.internvl_single --image-path /path/to/image.jpg
   ```

See the README.md and RUNNING.md files for detailed usage instructions.