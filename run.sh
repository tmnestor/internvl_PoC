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

# Default to local environment
RUNTIME_ENV="local"

# Parse runtime environment option
for arg in "$@"; do
    case $arg in
        --remote)
            RUNTIME_ENV="remote"
            shift
            ;;
        --local)
            RUNTIME_ENV="local"
            shift
            ;;
    esac
done

echo "Running in $RUNTIME_ENV environment mode"

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

# Function to validate path based on the execution environment
validate_path() {
    local path_type=$1
    local path=$2
    
    # Skip validation for non-path variables
    if [[ $path != /* ]]; then
        # For model path this could be a HuggingFace ID
        if [[ $path_type == "MODEL_PATH" && $path != *"/"* ]]; then
            echo "Using HuggingFace model: $path"
            return 0
        fi
        echo "INFO: $path_type does not appear to be a path"
        return 0
    fi
    
    # Validate based on environment mode
    if [[ "$RUNTIME_ENV" == "local" ]]; then
        # For local environment, check if the path exists on the local filesystem
        if [[ $path == /home/jovyan/* ]]; then
            echo "WARNING: Remote path detected in local environment for $path_type: $path"
            echo "You may need to edit the .env file to set the correct local path"
            return 1
        elif [ ! -d "$path" ] && [ ! -f "$path" ]; then
            echo "WARNING: Path for $path_type not found at $path"
            echo "You may need to:"
            echo "  1. Edit the .env file to set the correct path"
            echo "  2. Create the directory or file at the specified location"
            return 1
        else
            echo "Using local path for $path_type: $path"
            return 0
        fi
    elif [[ "$RUNTIME_ENV" == "remote" ]]; then
        # For remote environment, expect paths to be on the remote server
        if [[ $path == /home/jovyan/* ]]; then
            echo "Using remote path for $path_type: $path"
            return 0
        elif [[ $path == /Users/* ]]; then
            echo "WARNING: Local path detected in remote environment for $path_type: $path"
            echo "You may need to edit the .env file to set the correct remote path"
            return 1
        else
            echo "Using path for $path_type: $path"
            echo "Note: Path will be validated during runtime on the remote server"
            return 0
        fi
    fi
}

# Ensure output directory exists
mkdir -p "${PROJECT_DIR}/output"

# Validate core paths
echo "Validating paths for $RUNTIME_ENV environment..."

# Define the paths to validate
declare -a paths_to_validate=(
    "INTERNVL_PATH"
    "MODEL_PATH"
    "DATA_PATH"
    "OUTPUT_PATH"
    "IMAGE_FOLDER_PATH"
    "PROMPTS_PATH"
)

# Validate each path
for path_type in "${paths_to_validate[@]}"; do
    env_var="INTERNVL_${path_type}"
    # Handle special case for INTERNVL_PATH which doesn't have the INTERNVL_ prefix
    if [[ $path_type == "INTERNVL_PATH" ]]; then
        env_var="INTERNVL_PATH"
        path_type="PROJECT_PATH"
    fi
    
    # Get path from .env file
    path_value=$(grep "${env_var}=" "${PROJECT_DIR}/.env" | cut -d'=' -f2)
    
    if [[ ! -z "$path_value" ]]; then
        validate_path "$path_type" "$path_value"
    fi
done

# Check for arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 [--local|--remote] <command> [arguments] [--quiet|-q]"
    echo ""
    echo "Environment Mode:"
    echo "  --local    - Run in local environment mode (default)"
    echo "  --remote   - Run in remote environment mode"
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
    echo "  $0 --remote single --image-path /path/to/image.jpg"
    echo "  $0 --local single --image-path /path/to/image.jpg --quiet"
    exit 1
fi

# First argument is the command (after any environment flags)
COMMAND=$1
shift

# Check for --quiet flag and filter it out from args
QUIET_MODE=false
NEW_ARGS=()
for arg in "$@"; do
    if [ "$arg" == "--quiet" ] || [ "$arg" == "-q" ]; then
        QUIET_MODE=true
    elif [ "$arg" == "--local" ] || [ "$arg" == "--remote" ]; then
        # Environment flags already processed, ignore them here
        continue
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