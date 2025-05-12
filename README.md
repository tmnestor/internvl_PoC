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
# Required environment variables (absolute paths)
PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC  # Set to your project root path
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

This system can be run in two ways: via the run.sh script or by directly executing Python modules. For remote execution environments, both approaches work equally well.

### Running Python Modules Directly (Recommended for Remote Environments)

For the most control and flexibility in remote environments, you can execute the Python modules directly:

```bash
# Load all environment variables from .env file silently (including PYTHONPATH)
# Make sure your .env file contains: PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1

# Run a module (examples with common operations)
# Process a single image
python3 -m src.scripts.internvl_single --image-path /home/jovyan/nfs_share/username/internvl_PoC/test_receipt.png

# Process multiple images in batch mode
python3 -m src.scripts.internvl_batch --image-folder-path /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images

# Generate predictions for all images in a directory
python3 -m src.scripts.generate_predictions \
  --test-image-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images \
  --output-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_test

# Evaluate extraction performance
python3 -m src.scripts.evaluate_extraction \
  --predictions-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_test \
  --ground-truth-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/ground_truth
```

The environment variable loading command works as follows:
- `grep -v '^#' .env` - Filters out comment lines from the .env file
- `sed 's/^/export /'` - Adds "export " to the beginning of each line
- `source <( ... ) > /dev/null 2>&1` - Sources the commands silently into your shell
- This ensures that shell variables like `${INTERNVL_PATH}` in the .env file are properly expanded

### Using the run.sh Script (Alternative Approach)

The `run.sh` script provides automatic environment setup and is particularly useful when switching between environments:

```bash
# Process a single image
./scripts/run.sh --remote single --image-path /home/jovyan/nfs_share/username/internvl_PoC/test_receipt.png

# Process multiple images
./scripts/run.sh --remote batch --image-folder-path /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images

# Generate predictions
./scripts/run.sh --remote predict \
  --test-image-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images \
  --output-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_test

# Evaluate extraction results
./scripts/run.sh --remote evaluate \
  --predictions-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_test \
  --ground-truth-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/ground_truth
```

The `--remote` flag is important for remote execution as it automatically overrides these paths:
- `INTERNVL_PATH=/home/jovyan/nfs_share/tod/internvl_PoC`
- `INTERNVL_MODEL_PATH=/home/jovyan/nfs_share/models/huggingface/hub/InternVL2_5-1B`
- `INTERNVL_DATA_PATH=/home/jovyan/nfs_share/tod/internvl_PoC/data`
- `INTERNVL_OUTPUT_PATH=/home/jovyan/nfs_share/tod/internvl_PoC/output`
- `INTERNVL_PROMPTS_PATH=/home/jovyan/nfs_share/tod/internvl_PoC/prompts.yaml`

> **Important**: For the examples above, replace `/home/jovyan/nfs_share/username/` with your actual remote path.

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

## Command Examples for Remote Environments

Here are detailed examples of running different tasks in remote environments, showing both direct Python module execution and the run.sh script approach:

### Processing Single Images

```bash
# Option 1: Using Python module directly
# Make sure your .env file contains: PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1
python3 -m src.scripts.internvl_single --image-path /home/jovyan/nfs_share/username/internvl_PoC/test_receipt.png

# Option 2: Using run.sh
./scripts/run.sh --remote single --image-path /home/jovyan/nfs_share/username/internvl_PoC/test_receipt.png
```

### Processing Multiple Images (Batch Mode)

```bash
# Option 1: Using Python module directly
# Make sure your .env file contains: PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1
python3 -m src.scripts.internvl_batch --image-folder-path /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images

# Option 2: Using run.sh
./scripts/run.sh --remote batch --image-folder-path /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images
```

### Generating Predictions for a Dataset

```bash
# Option 1: Using Python module directly
# Make sure your .env file contains: PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1
python3 -m src.scripts.generate_predictions \
  --test-image-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images \
  --output-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_sroie

# Option 2: Using run.sh
./scripts/run.sh --remote predict \
  --test-image-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images \
  --output-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_sroie
```

### Evaluating Extraction Performance

```bash
# Option 1: Using Python module directly
# Make sure your .env file contains: PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1
python3 -m src.scripts.evaluate_extraction \
  --predictions-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_sroie \
  --ground-truth-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/ground_truth

# Option 2: Using run.sh
./scripts/run.sh --remote evaluate \
  --predictions-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_sroie \
  --ground-truth-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/ground_truth
```

> **Important**: Replace `/home/jovyan/nfs_share/username/` with your actual remote path. You may want to create a shorthand variable for readability in your scripts:
> ```bash
> REMOTE_ROOT=/home/jovyan/nfs_share/username/internvl_PoC
> python3 -m src.scripts.internvl_single --image-path $REMOTE_ROOT/test_receipt.png
> ```


## SROIE Dataset Evaluation

This project includes tools to evaluate the InternVL model on the SROIE receipt dataset. The SROIE dataset consists of real-world receipts with annotations for key fields like date, store name, tax, total, and line items.

### Dataset Structure

The SROIE dataset is located in the `data/sroie` directory with the following structure:
- `data/sroie/images/*.jpg` - Receipt images
- `data/sroie/ground_truth/*.json` - Ground truth files with labeled fields

### Running SROIE Evaluation in a Remote Environment

There are two ways to evaluate the SROIE dataset in a remote environment:

#### Option 1: Using Python Modules Directly

```bash
# Setup environment
# Make sure your .env file contains: PYTHONPATH=/home/jovyan/nfs_share/username/internvl_PoC
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1

# Step 1: Generate predictions for all SROIE images
python3 -m src.scripts.generate_predictions \
  --test-image-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/images \
  --output-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_sroie

# Step 2: Evaluate the predictions against ground truth
python3 -m src.scripts.evaluate_extraction \
  --predictions-dir /home/jovyan/nfs_share/username/internvl_PoC/output/predictions_sroie \
  --ground-truth-dir /home/jovyan/nfs_share/username/internvl_PoC/data/sroie/ground_truth
```

#### Option 2: Using the evaluate_sroie.sh Script

For convenience, you can use the included evaluation script which performs both steps:

```bash
# First, edit the script to use remote mode
sed -i 's/MODE="--local"/MODE="--remote"/' scripts/evaluate_sroie.sh

# Then run the script
./scripts/evaluate_sroie.sh
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