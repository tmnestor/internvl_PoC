#!/bin/bash
# ======================================================================
# InternVL Evaluation - Runner Script
# ======================================================================
# This script runs the InternVL evaluation scripts by:
# 1. Setting up the PYTHONPATH to find the package modules
# 2. Creating a default .env file if one doesn't exist
# 3. Running the scripts as Python modules with proper imports
#
# IMPORTANT: All scripts use the src.internvl import path pattern
# to maintain compatibility when running as Python modules.

# Set absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include the project directory
# This tells Python to look for modules in the project directory first
export PYTHONPATH="${PROJECT_DIR}"

# Function to validate required environment variables
validate_env() {
    local missing_vars=()
    local required_vars=(
        "INTERNVL_DATA_PATH"
        "INTERNVL_OUTPUT_PATH"
        "INTERNVL_MODEL_PATH"
        "INTERNVL_PROMPTS_PATH"
        "INTERNVL_IMAGE_FOLDER_PATH"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "ERROR: Missing required environment variables in .env file:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo "Please update your .env file with these required variables."
        exit 1
    fi
}

# Minimal environment info
echo "Project: $(basename "${PROJECT_DIR}") | PYTHONPATH: Set"

# Source the .env file to load environment variables
echo "Loading environment variables from .env file..."
# Convert .env file to a temp shell script for sourcing
grep -v '^#' ${PROJECT_DIR}/.env | sed 's/^/export /' > ${PROJECT_DIR}/.env.sh.tmp
source ${PROJECT_DIR}/.env.sh.tmp > /dev/null 2>&1
rm ${PROJECT_DIR}/.env.sh.tmp

# Validate that required environment variables are set
validate_env

# Debug: Print only the count of INTERNVL_ environment variables without full listing
INTERNVL_COUNT=$(env | grep -c INTERNVL_ || echo 0)
echo "Found $INTERNVL_COUNT INTERNVL_ environment variables"

# Check that .env file exists
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo "ERROR: .env file not found in project directory (${PROJECT_DIR})"
    echo "You must create a .env file with your configuration before running this script."
    echo "See README.md for required environment variables."
    echo ""
    echo "Required environment variables include:"
    echo "  INTERNVL_DATA_PATH          - Path to data directory"
    echo "  INTERNVL_OUTPUT_PATH        - Path to output directory"
    echo "  INTERNVL_MODEL_PATH         - Path to model or model ID"
    echo "  INTERNVL_PROMPTS_PATH       - Path to prompts YAML file"
    echo "  INTERNVL_IMAGE_FOLDER_PATH  - Path to image folder"
    echo ""
    echo "Example .env file:"
    echo "  INTERNVL_DATA_PATH=/path/to/data"
    echo "  INTERNVL_OUTPUT_PATH=/path/to/output"
    echo "  INTERNVL_MODEL_PATH=/path/to/model"
    echo "  INTERNVL_PROMPTS_PATH=/path/to/prompts.yaml"
    echo "  INTERNVL_IMAGE_FOLDER_PATH=/path/to/images"
    exit 1
fi

# (function moved to beginning of script)

# Ensure output directory exists
mkdir -p "${PROJECT_DIR}/output"

# Get model path from .env file
MODEL_PATH=$(grep "INTERNVL_MODEL_PATH" "${PROJECT_DIR}/.env" | cut -d'=' -f2)

# Check if model path exists (if it's a local path)
if [[ $MODEL_PATH != *"/"* ]]; then
    # Looks like a HuggingFace model ID, so that's fine
    echo "Using HuggingFace model: $MODEL_PATH"
elif [ ! -d "$MODEL_PATH" ]; then
    echo "WARNING: Model directory not found at $MODEL_PATH"
    echo "You may need to:"
    echo "  1. Edit the .env file to set the correct INTERNVL_MODEL_PATH"
    echo "  2. Download the model to the specified location"
    echo "  3. Or use a HuggingFace model ID (e.g., 'OpenGVLab/InternVL2_5-1B')"
fi

# Check for arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <command> [arguments] [--quiet|-q]"
    echo ""
    echo "Commands:"
    echo "  single     - Process a single image"
    echo "  batch      - Process images in batch"
    echo "  predict    - Generate predictions"
    echo "  evaluate   - Evaluate extraction results"
    echo ""
    echo "Options:"
    echo "  --quiet, -q  - Run with minimal output (suppress logging messages, Python warnings, etc.)"
    echo ""
    echo "Examples:"
    echo "  $0 single --image-path /path/to/image.jpg"
    echo "  $0 single --image-path /path/to/image.jpg --quiet"
    exit 1
fi

# First argument is the command
COMMAND=$1
shift

# Check for --quiet flag and filter it out from args
QUIET_MODE=false
NEW_ARGS=()
for arg in "$@"; do
    if [ "$arg" == "--quiet" ] || [ "$arg" == "-q" ]; then
        QUIET_MODE=true
    else
        NEW_ARGS+=("$arg")
    fi
done
set -- "${NEW_ARGS[@]}"  # Replace original arguments with filtered ones

# Map to the Python module path
PYTHON_MODULE=""
case $COMMAND in
    single)
        PYTHON_MODULE="src.scripts.internvl_single"
        ;;
    batch)
        PYTHON_MODULE="src.scripts.internvl_batch"
        ;;
    predict)
        PYTHON_MODULE="src.scripts.generate_predictions"
        ;;
    evaluate)
        PYTHON_MODULE="src.scripts.evaluate_extraction"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        exit 1
        ;;
esac

# Run the module with Python, passing all remaining arguments
echo "Running $PYTHON_MODULE..."

# Check if we're in a conda environment
if [ -n "$CONDA_PREFIX" ]; then
    echo "Using conda environment: $CONDA_PREFIX"
    if [ "$QUIET_MODE" = true ]; then
        # Completely silent mode with only critical errors
        export PYTHONWARNINGS="ignore"  # Suppress Python warnings
        python -m "$PYTHON_MODULE" "$@" 2>&1 | grep -v -E "INFO|DEBUG|WARNING"
    else
        python -m "$PYTHON_MODULE" "$@"
    fi
else
    # Try to use system Python or activate conda environment
    if command -v conda &> /dev/null; then
        echo "Activating conda environment 'internvl_env'..."
        # Source conda for this shell session
        eval "$(conda shell.bash hook)"
        conda activate internvl_env
        
        # Check for and install required packages
        echo "Checking for required packages..."
        if ! python -c "import einops" 2>/dev/null; then
            echo "Installing einops package (required by InternVL model)..."
            pip install einops
        fi
        
        # Now run with the environment's Python
        if [ "$QUIET_MODE" = true ]; then
            # Completely silent mode with only critical errors
            export PYTHONWARNINGS="ignore"  # Suppress Python warnings
            python -m "$PYTHON_MODULE" "$@" 2>&1 | grep -v -E "INFO|DEBUG|WARNING"
        else
            python -m "$PYTHON_MODULE" "$@"
        fi
    else
        # Fall back to system Python and warn
        echo "WARNING: Running with system Python (conda not found)"
        if command -v python3 &> /dev/null; then
            if [ "$QUIET_MODE" = true ]; then
                export PYTHONWARNINGS="ignore"  # Suppress Python warnings
                python3 -m "$PYTHON_MODULE" "$@" 2>&1 | grep -v -E "INFO|DEBUG|WARNING"
            else
                python3 -m "$PYTHON_MODULE" "$@"
            fi
        elif command -v python &> /dev/null; then
            if [ "$QUIET_MODE" = true ]; then
                export PYTHONWARNINGS="ignore"  # Suppress Python warnings
                python -m "$PYTHON_MODULE" "$@" 2>&1 | grep -v -E "INFO|DEBUG|WARNING"
            else
                python -m "$PYTHON_MODULE" "$@"
            fi
        else
            echo "ERROR: Python not found. Please install Python or activate conda environment."
            exit 1
        fi
    fi
fi
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Command completed successfully!"
    exit 0
else
    echo "Command failed with exit code $EXIT_CODE"
    echo "Check the error messages above for details."
    exit $EXIT_CODE
fi