# Setup Instructions for InternVL Synthetic

This document provides instructions for setting up the InternVL environment with Australian synthetic receipt data.

## 1. Conda Environment

The conda environment `internvl_env` is already created at:
```
/opt/homebrew/Caskroom/miniforge/base/envs/internvl_env
```

If you need to update the environment with any new dependencies, run:
```bash
conda env update -f environment.yml --prune
```

## 2. Activate the Environment

```bash
conda activate internvl_env
```

## 3. Directory Structure

The project is configured with the following directory structure:

- `/Users/tod/Desktop/internvl_synthetic/data/synthetic/` - Contains synthetic data
  - `train/images/` - Training images
  - `test/images/` - Test images
  - `val/images/` - Validation images
- `/Users/tod/Desktop/internvl_synthetic/models/` - Model files
- `/Users/tod/Desktop/internvl_synthetic/output/` - Output files
  - `predictions_test/` - Test predictions

## 4. Environment Configuration

The `.env` file has been configured with absolute paths for your machine.

## 5. Using the Notebooks

The following notebooks are available:

- `InternVL_Single.ipynb` - Process a single image with InternVL
- `InternVL_Batch.ipynb` - Process multiple images in batch mode
- `generate_predictions.ipynb` - Generate predictions for test data
- `evaluate_extraction.ipynb` - Evaluate extraction results with Australian-specific metrics

## 6. Generating Synthetic Data

To generate synthetic Australian receipts, use the scripts in the `data/generators/` directory:

```bash
# Activate the conda environment
conda activate internvl_env

# Navigate to the generators directory
cd /Users/tod/Desktop/internvl_synthetic/data/generators

# Generate sample receipts
python receipt_generator.py \
  --output_dir ../synthetic/test/images \
  --metadata_output ../synthetic/test/metadata \
  --num_receipts 10 \
  --australian \
  --include_gst
```

See the README in the `data/generators/` directory for more options and details.

## 7. Testing the Setup

To validate your setup, run the following steps:

1. Generate test receipt images using the script above
2. Run the `InternVL_Single.ipynb` notebook with one of these images
3. Verify that the GST (Australian tax) is correctly identified

Sample command for quick test:
```bash
# Generate one sample receipt for testing
python /Users/tod/Desktop/internvl_synthetic/data/generators/receipt_generator.py \
  --output_dir /Users/tod/Desktop/internvl_synthetic/data/synthetic/test/images \
  --metadata_output /Users/tod/Desktop/internvl_synthetic/data/synthetic/test/metadata \
  --num_receipts 1 \
  --australian \
  --include_gst
```

## Troubleshooting

- If you encounter CUDA issues, check that your PyTorch installation matches your CUDA version
- If paths are not resolving correctly, verify the absolute paths in the `.env` file
- For module import errors, ensure you're using the correct conda environment