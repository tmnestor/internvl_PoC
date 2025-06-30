# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This project uses conda for environment management due to PyTorch/CUDA dependencies:

```bash
# Create environment
conda env create -f internvl_env.yml

# Activate environment
conda activate internvl_env

# Update environment
conda env update -f internvl_env.yml --prune
```

**Important**: This project requires conda (not uv) due to complex GPU/ML dependencies. The environment configuration in `internvl_env.yml` supports both Mac development (CPU-only) and production GPU environments.

## Configuration Management

The project uses environment variables loaded from a `.env` file. All configuration is centralized in `src/internvl/config/config.py`.

Required environment variables (create `.env` file):
```bash
INTERNVL_PROJECT_ROOT=.
INTERNVL_DATA_PATH=data
INTERNVL_OUTPUT_PATH=output
INTERNVL_SOURCE_PATH=src
INTERNVL_PROMPTS_PATH=prompts.yaml
INTERNVL_MODEL_PATH=/path/to/model
INTERNVL_PROMPT_NAME=australian_optimized_prompt
```

## Module Invocation Pattern

**Critical**: All Python scripts MUST be executed using the module invocation pattern for KFP (Kubeflow Pipelines) compatibility:

```bash
# Load environment variables
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1

# Run scripts using module invocation
python -m internvl.cli.internvl_single --image-path test_receipt.png
python -m internvl.cli.internvl_batch --image-folder-path data/synthetic/images
python -m internvl.evaluation.generate_predictions --test-image-dir data/sroie/images --output-dir output/predictions
python -m internvl.evaluation.evaluate_extraction --predictions-dir output/predictions --ground-truth-dir data/sroie/ground_truth
```

## Core Architecture

### Package Structure
- `internvl/config/` - Configuration management and environment variable handling
- `internvl/model/` - Model loading and inference (`loader.py`, `inference.py`)
- `internvl/image/` - Image preprocessing and loading utilities
- `internvl/extraction/` - JSON extraction and field normalization pipeline
- `internvl/evaluation/` - Metrics calculation and evaluation framework
- `internvl/utils/` - Logging, path resolution, and common utilities
- `internvl/cli/` - Command-line interface scripts

### Key Components

**Model Loading** (`internvl/model/loader.py`):
- Handles both HuggingFace model IDs and local model paths
- Automatically detects GPU availability and configures device placement
- Supports FlashAttention optimization for GPU inference

**JSON Extraction Pipeline** (`internvl/extraction/`):
- `json_extraction.py` - Extracts structured JSON from model text output
- `normalization.py` - Normalizes Australian receipt fields (dates, prices, store names)

**Configuration System** (`internvl/config/config.py`):
- Centralized environment variable management with type conversion
- Path resolution for KFP compatibility
- Environment detection (development/staging/production)

## Prompt System

The project uses YAML-based prompt templates in `prompts.yaml`. Templates are optimized for Australian Tax Office receipts:

- `australian_optimized_prompt` - **DEFAULT**: Optimized for Australian GST/receipt formats with SROIE schema
- `default_receipt_prompt` - Standard extraction prompt
- `strict_json_prompt` - Enforces strict JSON-only output
- `huaifeng_receipt_json_prompt` - Original Huaifeng format (legacy compatibility)

## Testing and Evaluation

### Australian Synthetic Dataset Evaluation (Default)
```bash
# Generate predictions for Australian synthetic data
python -m internvl.evaluation.generate_predictions --test-image-dir data/synthetic/images --output-dir output/predictions_synthetic

# Evaluate results (uses synthetic data by default)
python -m internvl.evaluation.evaluate_extraction --show-examples
```

### SROIE Dataset Evaluation (Legacy)
```bash
# For non-Australian data comparison
python -m internvl.evaluation.evaluate_extraction \
    --predictions-dir output/predictions_sroie \
    --ground-truth-dir data/sroie/ground_truth \
    --output-path output/sroie_evaluation_results
```

### Custom Dataset Testing
```bash
# Generate predictions
python -m internvl.evaluation.generate_predictions --test-image-dir data/custom/images --output-dir output/predictions

# Evaluate results
python -m internvl.evaluation.evaluate_extraction --predictions-dir output/predictions --ground-truth-dir data/custom/ground_truth
```

## Development Guidelines

### Path Resolution
- All paths should be relative to `INTERNVL_PROJECT_ROOT`
- Use `internvl.utils.path.resolve_path()` for consistent path handling
- Model paths are typically absolute and may point to external volumes

### GPU/CPU Handling
- Model loading automatically detects CUDA availability
- Fallback mechanisms handle CPU-only environments
- Environment variable `CUDA_VISIBLE_DEVICES` can restrict GPU usage

### Logging
- Centralized logging in `internvl.utils.logging`
- Configurable log levels via environment variables
- Transformers library warnings can be controlled via `INTERNVL_TRANSFORMERS_LOG_LEVEL`

### Adding New Scripts
- Place in `internvl/cli/` or `internvl/evaluation/` directories as appropriate
- Use `internvl.config.setup_argparse()` for consistent argument parsing
- Follow module invocation pattern (executable via `python -m internvl.module.script_name`)
- Import from `internvl.*` modules

## Multi-User Environment Considerations

This project supports shared conda environments on multi-user systems:

```bash
# User-specific environment
conda config --append envs_dirs ~/.conda/envs
conda env create -f internvl_env.yml --prefix ~/.conda/envs/internvl_env

# Shared environment (if applicable)
conda config --append envgs_dirs /efs/shared/.conda/envs
conda env update -f internvl_env.yml --prefix /efs/shared/.conda/envs/internvl_env --prune
```

See `docs/SHARED_ENVIRONMENTS.md` for detailed multi-user setup instructions.

## Development Best Practices

- Always run the pre-commit ruff check before committing code

## Memories

- I am talking locally but running remotely