#!/bin/bash
# Script to create a clean package of the internvl_PoC project for offline migration
# This excludes large data files, environments, and other unnecessary elements

# Get the script directory and calculate project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default location for the output package
PACKAGE_DIR="${1:-"$PROJECT_ROOT/internvl_package"}"
PACKAGE_NAME="internvl_package.tar.gz"

echo "Creating clean package structure in: $PACKAGE_DIR"

# Create a temporary directory for the package
mkdir -p "$PACKAGE_DIR"

# Run the create_project_structure.sh script to establish the directory structure
"$SCRIPT_DIR/create_project_structure.sh" "$PACKAGE_DIR"

# Create a .gitignore file to exclude specific files/directories for the offline environment
cat > "$PACKAGE_DIR/.gitignore" << 'EOF'
# Python compiled files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution / packaging
dist/
build/
*.egg-info/

# Virtual environments
venv/
env/
ENV/
.env

# Local development settings
.vscode/
.idea/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# Environments
.env.local
.env.*.local

# Logs
logs/
*.log

# Output directories (but keep the structure)
output/*
!output/.gitkeep

# Large data files (keep directory structure)
*.jpg
*.png
*.jpeg
*.bmp
*.gif
*.tif*
*.webp
*.mp4
*.avi
*.mov
*.zip
*.tar*
*.gz
*.rar
*.7z
*.weights
*.pt
*.pth
*.pkl
*.h5
EOF

# Create .gitkeep files to preserve empty directories
find "$PACKAGE_DIR" -type d -empty -exec touch {}/.gitkeep \;

# Create a README file specifically for migration
cat > "$PACKAGE_DIR/MIGRATION_INSTRUCTIONS.md" << 'EOF'
# InternVL Migration Instructions

This package contains the InternVL project structure for migration to an offline environment.

## Package Contents

- Source code (`src/`)
- Scripts (`scripts/`)
- Documentation (`docs/`)
- Configuration files (YAML, environment examples)
- Directory structure (for data and outputs)

## Files You Need to Add Separately

These files should be transferred separately due to their size:

1. **Model Files**:
   - InternVL2.5 model files (typically several GB)
   - Add them to an appropriate directory in your offline environment
   - Update the model path in your .env file

2. **Dataset Files**:
   - SROIE dataset images (add to `data/sroie/images/`)
   - SROIE ground truth files (add to `data/sroie/ground_truth/`)
   - Synthetic dataset (add to appropriate directories under `data/synthetic/`)

3. **Environment Dependencies**:
   - If your offline environment doesn't have internet access, you'll need to download
     the Python packages specified in internvl_env.yml beforehand
   - Consider using conda-pack or a similar tool to bundle your environment

## Migration Steps

1. Transfer this package to your offline environment
   ```bash
   scp internvl_package.tar.gz user@offline-server:/path/to/destination/
   ```

2. Extract the package
   ```bash
   tar -xzf internvl_package.tar.gz
   cd internvl_package
   ```

3. Follow the instructions in OFFLINE_SETUP.md to complete the setup

## Maintaining the Offline Environment

- Document any changes made in the offline environment
- If updates are needed, create a reverse migration package to bring changes back online
- Consider setting up a version control system in your offline environment

EOF

# Create a tar.gz file of the package directory
echo "Creating tar.gz archive of the package..."
cd "$(dirname "$PACKAGE_DIR")"
tar -czf "$PACKAGE_NAME" "$(basename "$PACKAGE_DIR")"

echo "Package created successfully: $(realpath "$PACKAGE_NAME")"
echo "Package size: $(du -h "$PACKAGE_NAME" | cut -f1)"
echo ""
echo "Transfer this package to your offline environment and extract it."
echo "Follow the instructions in MIGRATION_INSTRUCTIONS.md to complete the setup."