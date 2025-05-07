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
mkdir -p ~/conda_envs
conda config --append envs_dirs ~/conda_envs

# Create the environment with a specific name for this project
# The --prefix option ensures it's created in your user directory
conda env create -f internvl_env.yml --prefix ~/conda_envs/internvl_env

# Activate the environment
conda activate ~/conda_envs/internvl_env
```

#### 2. Subsequent Activations

```bash
# Activate the environment in future sessions
conda activate ~/conda_envs/internvl_env
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
conda remove --prefix ~/conda_envs/internvl_env --all
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
chmod +x scripts/run.sh

# Process a single image
./scripts/run.sh single --image-path /path/to/image.jpg

# Process multiple images
./scripts/run.sh batch --image-folder-path /path/to/images

# Generate predictions
./scripts/run.sh predict --test-image-dir /path/to/data/synthetic/images --output-dir /path/to/output/predictions

# Evaluate extraction results
./scripts/run.sh evaluate --predictions-dir /path/to/output/predictions --ground-truth-dir /path/to/data/synthetic/ground_truth
```

#### Local vs Remote Execution

The `run.sh` script supports running in either local or remote environments. This is useful when developing locally but running the model on a remote server with different paths:

```bash
# Run in local environment mode (default)
./scripts/run.sh --local single --image-path /path/to/image.jpg

# Run in remote environment mode
./scripts/run.sh --remote single --image-path /path/to/image.jpg
```

The environment mode affects how paths are handled:
- **Local mode**: Uses paths as defined in .env file and validates they exist on the local filesystem
- **Remote mode**: Automatically overrides critical paths with remote-specific values
- **Path overrides**: In remote mode, these paths are hardcoded to remote values regardless of .env settings:
  - `INTERNVL_PATH=/home/jovyan/nfs_share/tod/internvl_PoC`
  - `INTERNVL_MODEL_PATH=/home/jovyan/nfs_share/models/huggingface/hub/InternVL2_5-1B`
- **Dual environment workflow**: This allows you to maintain a single .env file with local paths, but run in remote mode when executing on the server

This feature is especially useful when developing locally but executing on a remote server with different filesystem paths. You don't need to modify your .env file when switching between environments.

### Direct Python Module Execution (Recommended for Advanced Users)

For more control and transparency, you can run the Python modules directly:

```bash
# Set the PYTHONPATH to include the project directory
export PYTHONPATH=/path/to/project/root

# Process a single image
python -m src.scripts.internvl_single --image-path /path/to/image.jpg

# Process multiple images
python -m src.scripts.internvl_batch --image-folder-path /path/to/images

# Generate predictions
python -m src.scripts.generate_predictions --test-image-dir /path/to/data/synthetic/images --output-dir /path/to/output/predictions

# Evaluate extraction results
python -m src.scripts.evaluate_extraction --predictions-dir /path/to/output/predictions --ground-truth-dir /path/to/data/synthetic/ground_truth
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
├── data/                 # Data directories
│   └── synthetic/        # Synthetic data for testing
│       ├── ground_truth/ # Ground truth JSON files
│       └── images/       # Receipt images for testing
├── output/               # Output directory for results
├── tests/                # Unit tests
├── internvl_env.yml       # Conda environment specification
├── prompts.yaml          # Prompt templates for model extraction tasks
├── RUNNING.md            # Documentation for running commands
├── SHARED_COMPUTE.md     # Guide for running on shared compute resources
├── SETUP_INSTRUCTIONS.md # Setup instructions
├── scripts/             # Shell scripts
└── README.md             # This file
```

## License

[MIT License](LICENSE)

```bash
# Remote execution examples (with remote paths)
./run.sh --remote single --image-path /home/jovyan/nfs_share/tod/internvl_PoC/test_receipt.png
./run.sh --remote batch --image-folder-path /home/jovyan/nfs_share/tod/internvl_PoC/data/synthetic/images
./run.sh --remote predict --test-image-dir /home/jovyan/nfs_share/tod/internvl_PoC/data/synthetic/images --output-dir /home/jovyan/nfs_share/tod/internvl_PoC/output/predictions_test
./run.sh --remote evaluate --predictions-dir /home/jovyan/nfs_share/tod/internvl_PoC/output/predictions_test --ground-truth-dir /home/jovyan/nfs_share/tod/internvl_PoC/data/synthetic/ground_truth
```

## SROIE Dataset Evaluation

This project includes tools to evaluate the InternVL model on the SROIE receipt dataset. The SROIE dataset consists of real-world receipts with annotations for key fields like date, store name, tax, total, and line items.

### Preparation

The SROIE dataset is located in the `raechel_gold_images` directory with the following structure:
- `raechel_gold_images/*.jpg` - Receipt images
- `raechel_gold_images/ground_truth_sroie_v5.json` - Original ground truth data (in nested format)
- `raechel_gold_images/ground_truth/*.json` - Split ground truth files (created by the scripts)

Before evaluation, the ground truth data needs to be prepared (this has already been done):

1. Split the nested JSON file into individual files:
   ```bash
   ./scripts/split_json.sh
   ```

2. Fix any format issues:
   ```bash
   python3 fix_sroie_format.py
   python3 fix_null_files.py
   ```

### Running the Evaluation

The SROIE evaluation can be run with the provided script:

```bash
# For local execution
./scripts/evaluate_sroie.sh

# For remote execution - edit the script first to set MODE="--remote"
vim scripts/evaluate_sroie.sh  # Change MODE="--local" to MODE="--remote"
./scripts/evaluate_sroie.sh
```

The `evaluate_sroie.sh` script performs the following steps:
1. Generates predictions for all SROIE images
2. Evaluates the predictions against the ground truth files
3. Saves evaluation results to `output/evaluation_results.*`

### Remote Execution Notes

When running on a remote server:

1. Edit `evaluate_sroie.sh` to change the mode:
   ```bash
   # Change this line
   MODE="--remote"  # For remote execution
   ```

2. Make sure all paths in the script are absolute and point to the correct locations on the remote server.

3. Run the script:
   ```bash
   ./scripts/evaluate_sroie.sh
   ```

4. Results will be available in:
   - `output/evaluation_results.csv` - CSV format results
   - `output/evaluation_results.json` - Detailed JSON results
   - `output/evaluation_results.png` - Visualization of F1 scores by field

The evaluation compares your model's extraction performance on key fields:
- `date_value` - Date of the receipt
- `store_name_value` - Name of the store
- `tax_value` - Tax amount
- `total_value` - Total amount
- `prod_item_value` - Product names
- `prod_quantity_value` - Quantities
- `prod_price_value` - Prices