#!/bin/bash
# Script to create a Python venv with InternVL requirements

# Usage instructions
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: ./scripts/setup_venv.sh [venv_path]"
  echo "Creates a Python virtual environment with InternVL requirements"
  echo ""
  echo "Arguments:"
  echo "  venv_path    Path where the virtual environment will be created (default: ./venv)"
  exit 0
fi

# Set venv path (default or from argument)
VENV_PATH=${1:-"./venv"}
echo "Setting up Python venv at: $VENV_PATH"

# Create the venv
python3 -m venv "$VENV_PATH"
if [ $? -ne 0 ]; then
  echo "Error: Failed to create Python venv. Make sure Python 3 is installed."
  exit 1
fi

# Activate the venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  # Windows
  source "$VENV_PATH/Scripts/activate"
else
  # Linux/Mac
  source "$VENV_PATH/bin/activate"
fi

if [ $? -ne 0 ]; then
  echo "Error: Failed to activate the venv. Please check the path."
  exit 1
fi

echo "Python venv activated: $(which python)"

# Install core dependencies
echo "Installing core PyTorch dependencies..."
pip install torch==2.1.0 torchvision==0.16.0

echo "Installing InternVL dependencies..."
pip install transformers>=4.34.0 einops>=0.6.0

echo "Installing utility packages..."
pip install python-dotenv>=1.0.0 numpy<2.0.0 pillow>=9.4.0 pandas>=2.0.0 \
  dateparser>=1.1.8 nltk>=3.8.1 scikit-learn>=1.3.0 scikit-image>=0.21.0 \
  matplotlib>=3.7.0 opencv-python>=4.7.0 pyyaml>=6.0.0 tqdm>=4.65.0

echo "Installing development tools..."
pip install ipykernel>=6.0.0 ipywidgets>=8.0.0 ruff>=0.0.270 pytest>=7.3.1 pytest-cov>=4.1.0

# Create a requirements file for future installs
pip freeze > "$VENV_PATH/requirements.txt"
echo "Saved package list to $VENV_PATH/requirements.txt"

echo ""
echo "Virtual environment setup complete!"
echo ""
echo "To activate this environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  echo "source $VENV_PATH/Scripts/activate"
else
  echo "source $VENV_PATH/bin/activate"
fi
echo ""
echo "To deactivate when finished:"
echo "deactivate"