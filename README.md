# InternVL PoC - Receipt Information Extraction

A Python package for extracting structured information from images (particularly receipts/invoices) using InternVL3 multimodal models with automatic CPU/GPU configuration.

## Overview

InternVL PoC processes images to extract structured data fields like dates, store names, tax amounts, and products into JSON format. The system automatically detects and optimizes for available hardware (CPU, single GPU, or multi-GPU) and supports both local models and HuggingFace hosted models.

## Key Features

- **Auto Device Configuration**: Automatically detects and configures for CPU, single GPU, or multi-GPU setups
- **CPU-1GPU-MultiGPU Support**: Optimized configurations with 8-bit quantization for single GPU and device mapping for multi-GPU
- **Dynamic Image Processing**: Advanced image tiling and preprocessing for optimal model input
- **Structured JSON Extraction**: Robust extraction with field normalization for Australian receipts
- **Comprehensive Evaluation**: Metrics calculation with SROIE dataset support
- **Environment-based Configuration**: Uses `.env` files for flexible deployment
- **Modular Architecture**: Clean package structure for maintainability and deployment

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd internvl_PoC

# Create conda environment (required for PyTorch/GPU dependencies)
conda env create -f internvl_env.yml
conda activate internvl_env

# Configure environment variables
cp .env.example .env  # Edit with your paths
```

### 2. Configuration

Create/edit your `.env` file:

```bash
# Base configuration
INTERNVL_PROJECT_ROOT=.
INTERNVL_DATA_PATH=data
INTERNVL_OUTPUT_PATH=output
INTERNVL_SOURCE_PATH=internvl

# Model configuration (update with your model path)
INTERNVL_MODEL_PATH=/path/to/your/internvl3-8b/model

# Processing settings
INTERNVL_PROMPT_NAME=default_receipt_prompt
INTERNVL_IMAGE_SIZE=448
INTERNVL_MAX_TILES=8
INTERNVL_MAX_WORKERS=6
INTERNVL_MAX_TOKENS=1024
```

### 3. Basic Usage

```bash
# Process a single image
python -m internvl.cli.internvl_single --image-path test_receipt.png

# Process multiple images
python -m internvl.cli.internvl_batch --image-folder-path data/synthetic/images

# Run SROIE evaluation
python -m internvl.evaluation.evaluate_sroie
```

## Package Structure

```
internvl_PoC/
├── internvl/                    # Main package
│   ├── cli/                     # Command-line interfaces
│   │   ├── internvl_single.py   # Single image processing
│   │   └── internvl_batch.py    # Batch processing
│   ├── config/                  # Configuration management
│   ├── evaluation/              # Evaluation scripts and metrics
│   ├── extraction/              # JSON extraction and normalization
│   ├── image/                   # Image processing and preprocessing
│   ├── model/                   # Model loading and inference
│   └── utils/                   # Utilities and development tools
├── data/                        # Datasets
│   ├── sroie/                   # SROIE dataset
│   └── synthetic/               # Generated test data
├── docs/                        # Documentation
├── examples/                    # Example images
├── .env                         # Environment configuration
├── prompts.yaml                 # Prompt templates
├── internvl_codebase_demo.ipynb # Demo notebook
└── internvl_env.yml             # Conda environment
```

## Auto Device Configuration

The system automatically detects your hardware and applies optimal configurations:

### CPU-Only
- Uses `torch.float32` precision
- Optimized for development and testing

### Single GPU
- Uses `torch.bfloat16` precision with 8-bit quantization
- Optimal memory usage for large models

### Multi-GPU
- Distributes model layers across GPUs using device mapping
- Automatic load balancing for InternVL3-8B architecture

```python
# This happens automatically when loading models
from internvl.model.loader import load_model_and_tokenizer

model, tokenizer = load_model_and_tokenizer(
    model_path=config['model_path'],
    auto_device_config=True  # Enables automatic configuration
)
```

## Command-Line Interface

### Single Image Processing

```bash
# Basic usage
python -m internvl.cli.internvl_single --image-path path/to/receipt.jpg

# With custom output
python -m internvl.cli.internvl_single \
  --image-path data/synthetic/images/sample_receipt_001.jpg \
  --output-file output/result.json

# With verbose logging
python -m internvl.cli.internvl_single \
  --image-path test_receipt.png \
  --verbose
```

### Batch Processing

```bash
# Process all images in a directory
python -m internvl.cli.internvl_batch \
  --image-folder-path data/sroie/images

# With custom output and worker count
python -m internvl.cli.internvl_batch \
  --image-folder-path data/synthetic/images \
  --output-file output/batch_results.csv \
  --max-workers 4
```

## Evaluation and Testing

### SROIE Dataset Evaluation

```bash
# Run complete SROIE evaluation
python -m internvl.evaluation.evaluate_sroie

# Generate predictions only
python -m internvl.evaluation.generate_predictions \
  --test-image-dir data/sroie/images \
  --output-dir output/predictions

# Evaluate existing predictions
python -m internvl.evaluation.evaluate_extraction \
  --predictions-dir output/predictions \
  --ground-truth-dir data/sroie/ground_truth
```

### Custom Dataset Evaluation

```bash
# Evaluate your own dataset
python -m internvl.evaluation.evaluate_extraction \
  --predictions-dir output/my_predictions \
  --ground-truth-dir data/my_dataset/ground_truth \
  --show-examples
```

## Demo Notebook

The `internvl_codebase_demo.ipynb` notebook demonstrates the same functionality as the original Huaifeng_Test_InternVL.ipynb but using the structured codebase:

- Auto device detection and configuration
- Image processing with structured prompts
- JSON extraction and normalization
- Multiple test scenarios
- **Complete compatibility** with original Huaifeng notebook test cases

This notebook is ready to run at your workplace and will automatically detect and configure for available GPU resources. It includes all the original test prompts and can replicate the exact same functionality as the original notebook.

## Prompt System

The system uses YAML-based prompt templates in `prompts.yaml` with comprehensive coverage of different use cases:

### Australian Receipt Processing Prompts
```yaml
default_receipt_prompt: |
  <image>
  Extract information from this receipt and return in JSON format.
  Required fields: date_value, store_name_value, tax_value, total_value

australian_optimized_prompt: |
  <image>
  Extract these fields from the Australian receipt:
  1. date_value: Date in DD/MM/YYYY format
  2. store_name_value: Store name
  3. tax_value: GST amount (10%)
  4. total_value: Total amount including GST
  [Additional detailed instructions...]
```

### Original Huaifeng Notebook Prompts
The system now includes **all prompts from the original Huaifeng_Test_InternVL.ipynb**, ensuring complete compatibility:

```yaml
# Conference and business analysis
conference_relevance_prompt: |
  <image>
  Is this relevant to a claim about attending academic conference?

business_expense_prompt: |
  <image>
  Is this relevant to a claim about car expense?

# Receipt extraction (matching original notebook)
huaifeng_receipt_json_prompt: |
  <image>
  read the text and return information in JSON format. I need company name, address, phone number, date, ABN, and total amount

# Multi-receipt processing
multi_receipt_json_prompt: |
  <image>
  there are two receipts on this image. read the text and return information in JSON format. I need company name, address, phone number, date, ABN, and total amount

# Detailed item-level extraction
detailed_receipt_json_prompt: |
  <image>
  read the text and return information in JSON format. I need company name, address, phone number, date, item name, number of items, item price, and total amount
```

### Available Prompt Categories

| Category | Prompts | Use Case |
|----------|---------|----------|
| **Receipt Processing** | `default_receipt_prompt`, `australian_optimized_prompt` | Standard Australian receipt extraction |
| **Huaifeng Compatible** | `huaifeng_receipt_json_prompt`, `multi_receipt_json_prompt` | Exact replication of original notebook |
| **Business Analysis** | `business_expense_prompt`, `expense_relevance_prompt` | Expense claim relevance checking |
| **Conference/Meeting** | `conference_relevance_prompt`, `speaker_list_prompt` | Academic/conference document processing |
| **Detailed Extraction** | `detailed_receipt_json_prompt`, `strict_json_prompt` | Item-level detail extraction |
| **Generic** | `document_description_prompt`, `simple_receipt_prompt` | General document analysis |

### Using Prompts

Specify which prompt to use in your `.env` file:
```bash
# Use original Huaifeng prompts for compatibility
INTERNVL_PROMPT_NAME=huaifeng_receipt_json_prompt

# Use Australian-optimized prompts for production
INTERNVL_PROMPT_NAME=australian_optimized_prompt

# Use for conference document analysis
INTERNVL_PROMPT_NAME=conference_relevance_prompt
```

Or specify prompts dynamically in commands:
```bash
# Use specific prompt for single image
python -m internvl.cli.internvl_single \
  --image-path conference_program.jpg \
  --prompt-name conference_relevance_prompt

# Use multi-receipt prompt for batch processing
python -m internvl.cli.internvl_batch \
  --image-folder-path data/multi_receipts \
  --prompt-name multi_receipt_json_prompt
```

## Post-Processing Pipeline

### JSON Extraction
- Extracts structured JSON from model text output
- Handles multiple formats (markdown, raw JSON)
- Robust error handling and fallbacks

### Field Normalization
- **Dates**: Standardized to DD/MM/YYYY (Australian format)
- **Store Names**: Consistent capitalization and formatting
- **Prices**: Decimal standardization and currency handling
- **Text Fields**: Whitespace normalization

### Evaluation Metrics
- Field-level accuracy, precision, recall, F1-score
- Support for both scalar and list fields
- Comprehensive reporting and visualization

## Environment Management

### Local Development
```bash
conda activate internvl_env
python -m internvl.cli.internvl_single --image-path test.jpg
```

### Multi-User Systems
```bash
# User-specific environment
conda config --append envs_dirs ~/.conda/envs
conda env create -f internvl_env.yml --prefix ~/.conda/envs/internvl_env
conda activate ~/.conda/envs/internvl_env
```

### Shared Environments
See [docs/SHARED_ENVIRONMENTS.md](docs/SHARED_ENVIRONMENTS.md) for detailed setup instructions.

## Utilities

### Environment Verification
```bash
python -m internvl.utils.verify_env
```

### Development Tools
```bash
# Available in internvl.utils.dev_tools
python -m internvl.utils.dev_tools.test_path_resolution
python -m internvl.utils.dev_tools.test_image_resolution
```

## GPU Configuration

### Single GPU with Memory Constraints
```bash
# The system automatically applies 8-bit quantization
export CUDA_VISIBLE_DEVICES=0  # Use specific GPU
python -m internvl.cli.internvl_single --image-path test.jpg
```

### Multi-GPU Setup
```bash
# Automatic device mapping across all available GPUs
# No configuration needed - system detects and configures automatically
python -m internvl.cli.internvl_batch --image-folder-path data/images
```

## Deployment

### KFP (Kubeflow Pipelines) Compatibility
- Relative path support for container environments
- Environment variable-based configuration
- Module invocation pattern for consistent imports

See [docs/KFP_COMPATIBILITY.md](docs/KFP_COMPATIBILITY.md) for detailed deployment instructions.

## Contributing

When adding new features:
1. Follow the modular package structure
2. Add appropriate tests in the relevant module
3. Update documentation and examples
4. Ensure compatibility with auto device configuration

## Troubleshooting

### Common Issues

**Model Loading Errors**: Check your `INTERNVL_MODEL_PATH` in `.env`
```bash
python -m internvl.utils.verify_env  # Check environment setup
```

**GPU Memory Issues**: The system automatically applies quantization for single GPU setups
```bash
export CUDA_VISIBLE_DEVICES=0  # Limit to one GPU if needed
```

**Import Errors**: Ensure you're using the module invocation pattern:
```bash
python -m internvl.cli.internvl_single  # Correct
python internvl/cli/internvl_single.py  # Incorrect
```

**Path Resolution Issues**: Check your `.env` configuration and ensure `INTERNVL_PROJECT_ROOT` is set correctly.

## License

MIT License - see LICENSE file for details.