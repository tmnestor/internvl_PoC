# Maintaining Python Virtual Environments for InternVL

This document outlines best practices for maintaining and updating Python virtual environments for the InternVL project across multiple users.

## Initial Setup

Each user should create their own Python virtual environment using the provided setup script:

```bash
# Create a venv in the default location
./setup_venv.sh

# Or specify a custom location
./setup_venv.sh /path/to/custom/venv
```

## Environment Maintenance

### Updating Dependencies

When new dependencies are required or version updates are needed:

1. **Centralized Update Process**:
   - Designate one person as the environment maintainer
   - Update the `setup_venv.sh` script with the new dependencies
   - Push changes to the repository

2. **Communicating Changes**:
   - Create a notification system (e.g., Slack channel, email list) to inform users when dependency updates are made
   - Include a brief explanation of what changed and why

3. **User Update Process**:
   ```bash
   # Pull the latest changes
   git pull
   
   # Users have two options:
   
   # Option 1: Update existing environment
   source /path/to/venv/bin/activate
   pip install -r requirements-latest.txt
   
   # Option 2: Create a fresh environment
   # Backup any custom packages first
   pip freeze > my-custom-packages.txt
   # Remove the old environment
   rm -rf /path/to/venv
   # Create a new one
   ./setup_venv.sh /path/to/venv
   ```

### Managing Custom Dependencies

Users may need additional packages for their specific work:

1. **Document custom dependencies**:
   ```bash
   # Create a personal requirements file
   source /path/to/venv/bin/activate
   pip freeze > my-requirements.txt
   ```

2. **Separate core vs. custom packages**:
   - Maintain a central `requirements-core.txt` for required project dependencies
   - Each user can maintain a personal `requirements-custom.txt` 

3. **Proposing new core dependencies**:
   - If a custom package should become a core dependency, file a request 
   - Package requirements should be justified (usage purpose, compatibility)
   - Environment maintainer reviews and updates the setup script

## Version Control Considerations

1. **Do NOT commit virtual environments to version control**:
   - Add venv directories to `.gitignore`
   - Example: `/venv/`, `*.venv/`, `.env/`

2. **DO commit environment setup files**:
   - `setup_venv.sh`
   - `requirements-core.txt`

3. **Lock Files**:
   - For critical deployments, consider using lock files (e.g., `requirements-lock.txt`) 
   - Generated with exact versions: `pip freeze > requirements-lock.txt`
   - Useful for ensuring reproducible deployments

## Troubleshooting Common Issues

### Package Conflicts

If you encounter package conflicts:

1. Identify the conflicting packages:
   ```bash
   pip check
   ```

2. Try installing with the `--no-dependencies` flag:
   ```bash
   pip install some-package --no-dependencies
   ```

3. If problems persist, create a fresh environment

### Platform-Specific Issues

For teams working across different operating systems:

1. Maintain separate requirements files if needed:
   - `requirements-linux.txt`
   - `requirements-macos.txt`
   - `requirements-windows.txt`

2. Use platform checks in the setup script:
   ```bash
   if [[ "$OSTYPE" == "linux-gnu"* ]]; then
     # Linux-specific packages
     pip install linux-specific-package
   elif [[ "$OSTYPE" == "darwin"* ]]; then
     # macOS-specific packages
     pip install macos-specific-package
   fi
   ```

## Environment Verification

1. Create a verification script `verify_env.py`:
   ```python
   # verify_env.py
   import importlib
   import sys
   
   # List of required packages
   required_packages = [
       "torch", "transformers", "einops", "numpy", 
       "pandas", "dateparser", "nltk", "scikit-learn"
   ]
   
   def check_packages():
       missing = []
       for package in required_packages:
           try:
               importlib.import_module(package)
               print(f"✓ {package}")
           except ImportError:
               missing.append(package)
               print(f"✗ {package}")
       
       if missing:
           print(f"\nMissing packages: {', '.join(missing)}")
           return False
       else:
           print("\nAll required packages installed!")
           return True
           
   if __name__ == "__main__":
       sys.exit(0 if check_packages() else 1)
   ```

2. Run verification:
   ```bash
   python verify_env.py
   ```

## Shared Compute Environments

For teams sharing compute resources like remote servers or GPU machines:

1. **Shared Environment Location**:
   - Consider creating one shared environment in a central location
   - Document access permissions and usage policies
   - Example: `/opt/shared/internvl-venv/`

2. **Environment Modules**:
   - If your system uses environment modules, create a module file
   - Example: 
     ```
     #%Module
     setenv PYTHON_ENV_PATH /opt/shared/internvl-venv
     prepend-path PATH /opt/shared/internvl-venv/bin
     ```

3. **Resource Management**:
   - Include resource allocation information in documentation
   - Document GPU usage policies

## Backup Procedures

1. **Regular Backups**:
   ```bash
   # Back up just the package list
   pip freeze > backup-$(date +%Y%m%d).txt
   
   # Or create a full backup of the environment
   tar -czf venv-backup-$(date +%Y%m%d).tar.gz /path/to/venv
   ```

2. **Restore from Backup**:
   ```bash
   # Restore from package list
   python -m venv new-venv
   source new-venv/bin/activate
   pip install -r backup-20231012.txt
   ```

## Environment Activation in Scripts

To ensure scripts use the correct environment automatically:

1. **Shebang with explicit path** (most reliable):
   ```python
   #!/path/to/venv/bin/python
   
   import torch
   # rest of the script
   ```

2. **Embedded activation** (for bash scripts):
   ```bash
   #!/bin/bash
   source /path/to/venv/bin/activate
   
   # Now python commands use the venv
   python script.py
   ```

## Migrating from Conda

If migrating additional users from Conda to venv:

1. Export conda packages without builds:
   ```bash
   conda activate internvl_env
   conda list --export > conda-packages.txt
   ```

2. Convert to pip format:
   ```bash
   # Manual conversion needed for many packages
   # Sample script to help (will need manual verification)
   cat conda-packages.txt | grep -v "^#" | awk '{print $1"=="$2}' > requirements-from-conda.txt
   ```

3. Clean up the requirements file:
   - Remove conda-specific packages
   - Remove packages with complex build requirements
   - Fix version specifications

4. Create the new environment:
   ```bash
   python -m venv new-venv
   source new-venv/bin/activate
   pip install -r requirements-from-conda.txt
   ```