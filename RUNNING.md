# Running InternVL Commands

This document outlines different ways to run the InternVL scripts, depending on your preference and needs.

## Option 1: Direct Python Module Execution

If your environment is already properly set up, you can run the scripts directly as Python modules:

```bash
# Process a single image
python -m src.scripts.internvl_single --image-path /path/to/image.jpg

# Process a batch of images
python -m src.scripts.internvl_batch --image-folder-path /path/to/images

# Generate predictions
python -m src.scripts.generate_predictions --test-image-dir /path/to/test_images

# Evaluate extraction results
python -m src.scripts.evaluate_extraction --predictions-dir /path/to/predictions
```

**Advantages:**
- More explicit and transparent
- No shell script layer
- Follows standard Python module conventions
- Works the same way across all platforms
- Easily integrates with IDEs and debuggers

**Requirements:**
- Python environment must be already activated
- Environment variables must be already set (from .env file or directly)
- Required dependencies must be installed

## Option 2: Using the run.sh Script

The `run.sh` script provides a more convenient and managed approach:

```bash
# Process a single image
./run.sh single --image-path /path/to/image.jpg

# Process a batch of images
./run.sh batch --image-folder-path /path/to/images

# Generate predictions
./run.sh predict --test-image-dir /path/to/test_images

# Evaluate extraction results
./run.sh evaluate --predictions-dir /path/to/predictions

# Use the quiet mode for minimal output
./run.sh single --image-path /path/to/image.jpg --quiet
```

**Advantages:**
- Shorter commands
- Automatically loads environment variables from .env file
- Auto-detects and activates the conda environment
- Automatically installs missing dependencies
- Provides a quiet mode (--quiet or -q) for cleaner output
- Creates a consistent execution environment

**Requirements:**
- Bash shell (default on Linux/Mac, requires WSL or Git Bash on Windows)
- Execute permission on run.sh (`chmod +x run.sh`)

## Environment Requirements

For both approaches, the following environment setup is required:

1. Conda environment with Python 3.11:
   ```bash
   conda env create -f environment.yml
   conda activate internvl_env
   ```

2. Environment variables (either in .env file or set directly):
   ```
   INTERNVL_DATA_PATH=/path/to/data
   INTERNVL_OUTPUT_PATH=/path/to/output
   INTERNVL_MODEL_PATH=/path/to/model
   ```

## Choosing the Right Approach

- **Choose the direct Python module approach** if:
  - You prefer explicit commands
  - You're working in an IDE with debugging
  - You want to avoid shell script dependencies
  - You need cross-platform compatibility without modification

- **Choose the run.sh approach** if:
  - You prefer shorter commands
  - You want automatic environment activation
  - You want automatic dependency installation
  - You prefer a consistent execution environment
  - You want to use the quiet mode for cleaner output