# InternVL Evaluation 

A Python package for extracting structured information from images (particularly receipts/invoices) using InternVL2.5 multimodal models.

## Overview

InternVL Evaluation processes images to extract structured data fields like dates, store names, tax amounts, and products into JSON format. The system works with both local models and HuggingFace hosted models.

> **Note**: This project has been migrated from Jupyter notebooks to a proper Python package structure.

## Features

- Dynamic image tiling for optimal model input
- Single and batch processing modes
- Structured JSON output extraction
- Field normalization (dates, prices, store names)
- Comprehensive evaluation metrics
- CPU and GPU support
- Environment-aware configuration

## Installation

### Using Conda

```bash
# Clone the repository
git clone https://github.com/your-organization/internvl-evaluation.git
cd internvl-evaluation

# Create and activate the environment
conda env create -f environment.yml
conda activate internvl_env

# Create a .env file in the project root with required configuration
# All paths must be absolute, not relative
```

### Configuration

#### Environment Variables

The system requires a `.env` file for configuration. Create this file in the project root with the following required variables:

```bash
# Required environment variables (absolute paths)
INTERNVL_DATA_PATH=/path/to/data
INTERNVL_OUTPUT_PATH=/path/to/output
INTERNVL_IMAGE_FOLDER_PATH=/path/to/images
INTERNVL_MODEL_PATH=/path/to/model
INTERNVL_PROMPTS_PATH=/path/to/prompts.yaml

# Optional settings with defaults
INTERNVL_PROMPT_NAME=default_receipt_prompt
INTERNVL_IMAGE_SIZE=448
INTERNVL_MAX_TILES=8
INTERNVL_MAX_WORKERS=4
INTERNVL_MAX_TOKENS=1024
```

Note: If the `.env` file is missing or lacks required variables, the script will display an error message.

#### Prompt Templates

The `prompts.yaml` file contains templates for prompting the InternVL model. These templates specify how to ask the model to extract structured information from images. The system includes several pre-configured prompts:

- `default_receipt_prompt`: Standard prompt for extracting receipt data
- `simple_receipt_prompt`: Minimal prompt for basic extraction
- `strict_json_prompt`: Prompt enforcing strict JSON output format
- `detailed_receipt_prompt`: Extensive prompt with field explanations
- `australian_optimized_prompt`: Optimized for Australian receipts

The prompt to use is specified by the `INTERNVL_PROMPT_NAME` environment variable. You can modify existing prompts or add new ones by editing the `prompts.yaml` file.

Example prompt structure:
```yaml
default_receipt_prompt: |
  <image>
  Extract these fields from the provided receipt:
  1. date_value: The date of purchase
  2. store_name_value: The name of the store
  ...
  Return the results in a valid JSON format
```

## Usage

There are two ways to run InternVL scripts:

### Using the run.sh Script (Recommended for Beginners)

The `run.sh` script provides convenience features like automatic environment setup, dependency checks, and simplified commands:

```bash
# First, make the script executable
chmod +x run.sh

# Process a single image
./run.sh single --image-path /path/to/image.jpg

# Process multiple images
./run.sh batch --image-folder-path /path/to/images

# Generate test predictions
./run.sh predict --test-image-dir /path/to/test/images --output-dir /path/to/predictions

# Evaluate extraction results
./run.sh evaluate --predictions-dir /path/to/predictions --ground-truth-dir /path/to/ground_truth
```

### Direct Python Module Execution (Recommended for Advanced Users)

For more control and transparency, you can run the Python modules directly:

```bash
# Set the PYTHONPATH to include the project directory
export PYTHONPATH=/path/to/project/root

# Process a single image
python -m src.scripts.internvl_single --image-path /path/to/image.jpg

# Process multiple images
python -m src.scripts.internvl_batch --image-folder-path /path/to/images

# Generate test predictions
python -m src.scripts.generate_predictions --test-image-dir /path/to/test/images --output-dir /path/to/predictions

# Evaluate extraction results
python -m src.scripts.evaluate_extraction --predictions-dir /path/to/predictions --ground-truth-dir /path/to/ground_truth
```

The `-m` flag tells Python to run the module as a script, which ensures proper imports and package structure.

For a detailed comparison of both approaches, see [RUNNING.md](RUNNING.md).

## Documentation

The primary documentation for this project is in this README and the [RUNNING.md](RUNNING.md) file.

### Prompt System

The `prompts.yaml` file is central to the extraction functionality:

- **Purpose**: Contains templates that instruct the InternVL model how to extract structured data from images
- **Format**: YAML with multiple named prompt templates (e.g., `default_receipt_prompt`, `detailed_receipt_prompt`)
- **Usage**: The system uses the prompt specified by `INTERNVL_PROMPT_NAME` in your `.env` file
- **Customization**: Edit existing prompts or add new ones by modifying this file
- **Structure**: Each prompt includes an `<image>` placeholder and instructions for extracting specific fields
- **JSON Output**: All prompts are designed to instruct the model to return data in JSON format

This flexible prompt system allows you to tailor extraction for different document types or information needs without changing code.

## Testing

Run the test suite:

```bash
pytest
```

## Directory Structure

```
internvl-evaluation/
├── src/                  # Source code
│   ├── internvl/         # Core package
│   │   ├── config/       # Configuration management
│   │   ├── evaluation/   # Evaluation metrics
│   │   ├── extraction/   # JSON extraction and normalization
│   │   ├── image/        # Image processing
│   │   ├── model/        # Model loading and inference
│   │   └── utils/        # Utilities (logging, path management)
│   └── scripts/          # Command-line scripts
│       ├── internvl_single.py       # Process single image
│       ├── internvl_batch.py        # Process batch of images
│       ├── generate_predictions.py  # Generate predictions
│       └── evaluate_extraction.py   # Evaluate results
├── tests/                # Unit tests
├── environment.yml       # Conda environment specification
├── prompts.yaml          # Prompt templates for model extraction tasks
├── run.sh                # Helper script for running commands
├── RUNNING.md            # Documentation for running commands
├── SETUP_INSTRUCTIONS.md # Setup instructions
└── README.md             # This file
```

## License

[MIT License](LICENSE)

```bash
./run.sh single --image-path /home/jovyan/nfs_share/tod/internvl_PoC/test_receipt.png
./run.sh batch --image-folder-path /home/jovyan/nfs_share/tod/internvl_PoC/data/synthetic/test/images
./run.sh predict --test-image-dir /home/jovyan/nfs_share/tod/internvl_PoC/data/synthetic/test/images --output-dir /home/jovyan/nfs_share/tod/internvl_PoC/output/predictions_test
./run.sh evaluate --predictions-dir /home/jovyan/nfs_share/tod/internvl_PoC/output/predictions_test --ground-truth-dir /home/jovyan/nfs_share/tod/internvl_PoC/data/synthetic/test/ground_truth
```