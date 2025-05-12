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

## Kubeflow Pipelines (KFP) Compatibility

This system now supports Kubeflow Pipelines (KFP) compatibility through:

1. **Relative Path Support**: All paths can now be specified relative to the project root
2. **Module Invocation Pattern**: Enforces consistent import behavior across environments
3. **Environment Detection**: Automatically adapts to different execution environments

See the [KFP Compatibility Guide](docs/KFP_COMPATIBILITY.md) for detailed information.

### Setting Up Conda Environment on Multi-User Linux Systems

For multi-user Linux systems, it's important to set up isolated environments that don't interfere with other users while efficiently managing resources:

#### 1. Initial Setup (One-Time)

```bash
# Clone the repository
git clone https://github.com/tmnestor/internvl_PoC_.git
cd internvl_PoC

# Set up conda to use a user-specific environment directory
# This avoids permission issues in shared environments
mkdir -p ~/.conda/envs
conda config --append envs_dirs ~/.conda/envs

# Create the environment with a specific name for this project
# The --prefix option ensures it's created in your user directory
conda env create -f internvl_env.yml --prefix ~/.conda/envs/internvl_env

# Activate the environment
conda activate ~/.conda/envs/internvl_env
```

#### 2. Subsequent Activations

```bash
# Activate the environment in future sessions
conda activate ~/.conda/envs/internvl_env
```

#### 3. Environment Configuration

```bash
# Create a user-specific .env file
cp .env.example .env

# Edit the .env file with your specific paths
# All paths must be absolute, not relative
nano .env
```

#### 4. Handling Shared GPU Resources

If your system has GPUs that are shared among users:

```bash
# Check GPU availability and usage
nvidia-smi

# If needed, specify a particular GPU to use
export CUDA_VISIBLE_DEVICES=0  # Use only GPU 0
```

#### 5. Environment Cleanup (When Needed)

```bash
# Deactivate first
conda deactivate

# Remove the environment when no longer needed
conda remove --prefix ~/.conda/envs/internvl_env --all
```

This approach provides several advantages for multi-user systems:
- Each user maintains their own isolated environment
- Avoids permission issues with system-wide conda installations
- Prevents conflicts between different users' package requirements
- Allows for easier cleanup when the environment is no longer needed

### Configuration

#### Environment Variables

The system requires a `.env` file for configuration. Create this file in the project root with the following required variables:

```bash
# Project root path - base for all relative paths
INTERNVL_PROJECT_ROOT=.

# Required paths (relative to project root for KFP compatibility)
INTERNVL_DATA_PATH=data
INTERNVL_OUTPUT_PATH=output
INTERNVL_SOURCE_PATH=src
INTERNVL_PROMPTS_PATH=prompts.yaml

# Derived paths
INTERNVL_SYNTHETIC_DATA_PATH=${INTERNVL_DATA_PATH}/synthetic
INTERNVL_SROIE_DATA_PATH=${INTERNVL_DATA_PATH}/sroie
INTERNVL_IMAGE_FOLDER_PATH=${INTERNVL_SYNTHETIC_DATA_PATH}/images

# Path/name of the InternVL model to use (typically absolute)
INTERNVL_MODEL_PATH=/path/to/model  # This is often on a different drive

# Optional settings with defaults
INTERNVL_PROMPT_NAME=default_receipt_prompt
INTERNVL_IMAGE_SIZE=448
INTERNVL_MAX_TILES=8
INTERNVL_MAX_WORKERS=4
INTERNVL_MAX_TOKENS=1024
INTERNVL_TRANSFORMERS_LOG_LEVEL=ERROR  # Hide transformers warnings
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

This system is run by executing Python modules using the module invocation pattern, which ensures consistent imports and path resolution across all environments.

### Running Python Modules (Standard Approach)

The system uses the Python module invocation pattern for all operations, which provides consistent imports and path resolution:

```bash
# Load all environment variables from .env file silently
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1

# Process a single image
python -m src.scripts.internvl_single --image-path test_receipt.png

# Process multiple images in batch mode
python -m src.scripts.internvl_batch --image-folder-path data/synthetic/images

# Generate predictions for all images in a directory
python -m src.scripts.generate_predictions \
  --test-image-dir data/synthetic/images \
  --output-dir output/predictions_test

# Evaluate extraction performance
python -m src.scripts.evaluate_extraction \
  --predictions-dir output/predictions_test \
  --ground-truth-dir data/synthetic/ground_truth

# Run SROIE dataset evaluation
python -m src.scripts.evaluate_sroie

# Create project structure in a new location
python -m src.scripts.create_project_structure --target-dir /path/to/new/location

# Split SROIE ground truth into individual files
python -m src.scripts.split_json
```

The environment variable loading command works as follows:
- `grep -v '^#' .env` - Filters out comment lines from the .env file
- `sed 's/^/export /'` - Adds "export " to the beginning of each line
- `source <( ... ) > /dev/null 2>&1` - Sources the commands silently into your shell
- This ensures that shell variables are properly expanded

> **Important**: All commands use relative paths to the project root, which will be resolved based on the INTERNVL_PROJECT_ROOT environment variable. Make sure your .env file is properly configured.

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


## Directory Structure

```
internvl_PoC/
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
├── data/                 # Data directories
│   ├── generators/       # Scripts for generating synthetic data
│   ├── sroie/            # SROIE dataset
│   │   ├── ground_truth/ # Ground truth JSON files
│   │   └── images/       # Receipt images for testing
│   └── synthetic/        # Synthetic data for testing
│       ├── ground_truth/ # Ground truth JSON files
│       └── images/       # Receipt images for testing
├── docs/                 # Documentation
│   ├── RUNNING.md        # Documentation for running commands
│   ├── SETUP_INSTRUCTIONS.md # Setup instructions
│   ├── SHARED_COMPUTE.md # Guide for running on shared compute resources
│   ├── SHARED_ENVIRONMENTS.md # Guide for shared conda environments
│   └── VENV_MAINTENANCE.md # Environment maintenance guide
├── output/               # Output directory for results
│   └── predictions_test/ # Test predictions
├── scripts/              # Shell scripts
│   ├── run.sh                # Main runner script
│   ├── evaluate_sroie.sh     # Script to evaluate on SROIE dataset
│   ├── setup_venv.sh         # Script to set up virtual environment
│   └── create_clean_package.sh  # Script to create offline deployment package
├── internvl_env.yml      # Conda environment specification
├── prompts.yaml          # Prompt templates for model extraction tasks
├── PROJECT_OVERVIEW.md   # High-level project overview
├── README.md             # This file
└── verify_env.py         # Script to verify environment
```

## Command Examples

Here are detailed examples of running different tasks using the Python module invocation pattern:

### First, Set Up the Environment Variables

```bash
# Load environment variables
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1

# If needed, you can verify the paths are set correctly
echo "Project root: ${INTERNVL_PROJECT_ROOT}"
echo "Data path: ${INTERNVL_DATA_PATH}"
echo "Output path: ${INTERNVL_OUTPUT_PATH}"
```

### Processing Single Images

```bash
# Process a single receipt image
python -m src.scripts.internvl_single --image-path test_receipt.png

# Process with specific output file
python -m src.scripts.internvl_single --image-path data/synthetic/images/sample_receipt_001.jpg --output-file output/results/sample_001_result.json
```

### Processing Multiple Images (Batch Mode)

```bash
# Process all images in the SROIE dataset
python -m src.scripts.internvl_batch --image-folder-path data/sroie/images

# Process images in the synthetic dataset with a specific prompt
python -m src.scripts.internvl_batch --image-folder-path data/synthetic/images --prompt-name australian_optimized_prompt
```

### Generating Predictions for a Dataset

```bash
# Generate predictions for SROIE dataset
python -m src.scripts.generate_predictions \
  --test-image-dir data/sroie/images \
  --output-dir output/predictions_sroie

# Generate predictions for synthetic dataset with custom model path
python -m src.scripts.generate_predictions \
  --test-image-dir data/synthetic/images \
  --output-dir output/predictions_synthetic \
  --model-path /path/to/custom/model
```

### Evaluating Extraction Performance

```bash
# Evaluate SROIE predictions
python -m src.scripts.evaluate_extraction \
  --predictions-dir output/predictions_sroie \
  --ground-truth-dir data/sroie/ground_truth

# Evaluate synthetic predictions with examples shown
python -m src.scripts.evaluate_extraction \
  --predictions-dir output/predictions_synthetic \
  --ground-truth-dir data/synthetic/ground_truth \
  --show-examples
```

> **Important**: The examples above use relative paths to the project root, which will be resolved based on the INTERNVL_PROJECT_ROOT environment variable. Make sure your .env file is properly configured.


## SROIE Dataset Evaluation

This project includes tools to evaluate the InternVL model on the SROIE receipt dataset. The SROIE dataset consists of real-world receipts with annotations for key fields like date, store name, tax, total, and line items.

### Dataset Structure

The SROIE dataset is located in the `data/sroie` directory with the following structure:
- `data/sroie/images/*.jpg` - Receipt images
- `data/sroie/ground_truth/*.json` - Ground truth files with labeled fields

### Running SROIE Evaluation

You can evaluate the SROIE dataset using the dedicated Python module:

```bash
# Run the complete SROIE evaluation pipeline
python -m src.scripts.evaluate_sroie

# Run with specific options
python -m src.scripts.evaluate_sroie --prompt-name australian_optimized_prompt --show-examples
```

The evaluation pipeline consists of two steps:

1. Generate predictions for all SROIE images:
   ```bash
   python -m src.scripts.generate_predictions \
     --test-image-dir data/sroie/images \
     --output-dir output/predictions_sroie
   ```

2. Evaluate the predictions against ground truth:
   ```bash
   python -m src.scripts.evaluate_extraction \
     --predictions-dir output/predictions_sroie \
     --ground-truth-dir data/sroie/ground_truth
   ```

### Evaluation Results

After running the evaluation, results will be available in:
- `output/evaluation_results.csv` - CSV format results
- `output/evaluation_results.json` - Detailed JSON results
- `output/evaluation_results.png` - Visualization of F1 scores by field

The evaluation compares extraction performance on the following fields:
- `date_value` - Date of the receipt
- `store_name_value` - Name of the store
- `tax_value` - Tax amount
- `total_value` - Total amount
- `prod_item_value` - Product names
- `prod_quantity_value` - Quantities
- `prod_price_value` - Prices

Note: Make sure to run the evaluation script from the project root directory for proper path resolution.


## License

[MIT License](LICENSE)