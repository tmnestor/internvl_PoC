# InternVL Evaluation 

A Python package for extracting structured information from images (particularly receipts/invoices) using InternVL2.5 multimodal models.

## Overview

InternVL Evaluation processes images to extract structured data fields like dates, store names, tax amounts, and products into JSON format. The system works with both local models and HuggingFace hosted models.

> **Note**: This project has been migrated from Jupyter notebooks to a proper Python package structure.

## Features

- Dynamic image tiling for optimal model input
- Single and batch processing modes
- Structured JSON output extraction
- Post-Processing Pipeline:
  - Robust JSON extraction from model output text
  - Field normalization:
    - Dates to DD/MM/YYYY (Australian standard)
    - Store names (capitalization, whitespace handling)
    - Prices and currency values (decimal standardization)
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

# Edit the .env file with your specific paths and settings
# Use relative paths for KFP compatibility
nano .env

# Be sure to specify which prompt to use from prompts.yaml
# Example: INTERNVL_PROMPT_NAME=australian_optimized_prompt
```

#### 4. Handling Shared GPU Resources & Environments

If your system has GPUs that are shared among users:

```bash
# Check GPU availability and usage
nvidia-smi

# If needed, specify a particular GPU to use
export CUDA_VISIBLE_DEVICES=0  # Use only GPU 0
```

For managing shared conda environments in multi-user systems:

```bash
# Configure conda to use a shared environment location
conda config --append envs_dirs /efs/shared/.conda/envs

# Update the shared environment
conda env update -f internvl_env.yml --prefix /efs/shared/.conda/envs/internvl_env --prune

# Activate the shared environment
conda activate /efs/shared/.conda/envs/internvl_env
```

See [SHARED_ENVIRONMENTS.md](docs/SHARED_ENVIRONMENTS.md) for detailed information on managing shared conda environments.

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

# Verify environment setup
python -m src.scripts.utils.verify_env
```

The environment variable loading command works as follows:
- `grep -v '^#' .env` - Filters out comment lines from the .env file
- `sed 's/^/export /'` - Adds "export " to the beginning of each line
- `source <( ... ) > /dev/null 2>&1` - Sources the commands silently into your shell
- This ensures that shell variables are properly expanded

> **Important**: All commands use relative paths to the project root, which will be resolved based on the INTERNVL_PROJECT_ROOT environment variable. Make sure your .env file is properly configured.

## Documentation

The primary documentation for this project is in this README, the [KFP_COMPATIBILITY.md](docs/KFP_COMPATIBILITY.md) file, and the [SHARED_ENVIRONMENTS.md](docs/SHARED_ENVIRONMENTS.md) guide for managing shared conda environments.

### Post-Processing Pipeline

The post-processing pipeline is a critical component for extracting and standardizing data:

1. **JSON Extraction** (`src/internvl/extraction/json_extraction.py`):
   - Extracts structured JSON from the model's text output
   - Handles multiple JSON formats (markdown code blocks, raw JSON)
   - Provides fallback mechanisms for malformed JSON
   - Includes pattern matching for field identification

2. **Field Normalization** (`src/internvl/extraction/normalization.py`):
   - Standardizes dates to DD/MM/YYYY format using intelligent date parsing
   - Normalizes store names with consistent capitalization
   - Cleans numeric values by removing currency symbols and standardizing decimal formats
   - Handles edge cases in various data representations

3. **Evaluation System** (`src/internvl/evaluation/metrics.py`):
   - Calculates accuracy, precision, recall, and F1-score
   - Provides field-specific evaluation metrics
   - Supports both scalar fields (date, store, tax, total) and list fields (items, quantities, prices)
   - Generates visualizations and comprehensive reports

### Prompt System for Australian Tax Office Receipts

The `prompts.yaml` file is central to the extraction functionality and is designed to be customized when you have access to actual Australian Tax Office (ATO) receipts. This file contains specialized prompts that instruct the model on how to extract the required Australian tax receipt fields.

#### YAML Prompt Structure

The file contains multiple pre-configured prompts optimized for Australian receipts:

```yaml
# Default prompt for receipt information extraction
default_receipt_prompt: |
  <image>
  Extract these fields from the provided Australian receipt:
  1. date_value: The date of purchase (DD/MM/YYYY)
  2. store_name_value: The name of the Australian store or company
  3. tax_value: The GST (10% tax) amount
  4. total_value: The total purchase amount
  5. prod_item_value: List of product items purchased
  6. prod_quantity_value: List of quantities for each product
  7. prod_price_value: List of prices for each product

  # [Additional instructions and formatting guidance...]
```

#### Available Prompt Templates

1. **default_receipt_prompt**: Standard prompt with basic instructions
2. **simple_receipt_prompt**: Minimal prompt for basic extraction
3. **strict_json_prompt**: Prompt enforcing strict JSON output format
4. **detailed_receipt_prompt**: Extensive prompt with field explanations
5. **australian_optimized_prompt**: Optimized specifically for Australian receipts with detailed guidance

#### Customizing for ATO Receipts

When you have access to actual ATO receipts, you may need to modify the prompts:

1. **Field Alignment**: Make sure the field names match exactly what you need for ATO data
2. **Australian GST Handling**: Ensure proper extraction of GST (10%)
3. **Australian Date Formats**: Verify date extraction in DD/MM/YYYY format
4. **Field Detection**: Add specific hints about where fields typically appear on ATO receipts
5. **Required Fields**: Add or modify fields based on specific ATO requirements

To modify a prompt:

```bash
# Edit the prompts.yaml file
nano prompts.yaml

# Then specify which prompt to use in your .env file
INTERNVL_PROMPT_NAME=australian_optimized_prompt
```

#### Testing Modified Prompts

After modifying prompts for ATO receipts:

```bash
# Test your modified prompt with a single receipt
python -m src.scripts.internvl_single --image-path path/to/ato_receipt.jpg --prompt-name your_custom_prompt

# Compare different prompts to find which works best
python -m src.scripts.evaluate_extraction \
  --predictions-dir output/predictions_test_prompt1 \
  --ground-truth-dir data/ato/ground_truth \
  --output-path output/eval_prompt1
```

This flexible prompt system allows you to tailor extraction specifically for Australian tax receipts without changing any code.


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
│       ├── evaluate_extraction.py   # Evaluate results
│       ├── evaluate_sroie.py        # Run SROIE dataset evaluation
│       ├── split_json.py            # Split SROIE JSON into individual files
│       ├── create_project_structure.py  # Create project directory structure
│       └── utils/                  # Utility scripts
│           └── verify_env.py       # Verify environment setup
├── data/                 # Data directories
│   ├── generators/       # Scripts for generating synthetic data
│   ├── sroie/            # SROIE dataset
│   │   ├── ground_truth/ # Ground truth JSON files
│   │   └── images/       # Receipt images for testing
│   └── synthetic/        # Synthetic data for testing
│       ├── ground_truth/ # Ground truth JSON files
│       └── images/       # Receipt images for testing
├── docs/                 # Documentation
│   ├── KFP_COMPATIBILITY.md # Guide for Kubeflow Pipelines compatibility
│   └── SHARED_ENVIRONMENTS.md # Guide for managing shared conda environments
├── output/               # Output directory for results
│   └── predictions_test/ # Test predictions
├── scripts/              # Empty (legacy scripts removed)
├── internvl_env.yml      # Conda environment specification
├── prompts.yaml          # Prompt templates for model extraction tasks
├── PROJECT_OVERVIEW.md   # High-level project overview
└── README.md             # This file
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