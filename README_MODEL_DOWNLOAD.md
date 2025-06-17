# InternVL3-8B Model Download Guide

This guide provides comprehensive instructions for downloading the InternVL3-8B model from HuggingFace to a remote machine for offline use using the provided `huggingface_model_download.py` script.

## Overview

The InternVL3-8B model (https://huggingface.co/OpenGVLab/InternVL3-8B) is a large multimodal model that requires offline access in production environments without internet connectivity. This guide covers the complete process from initial setup to final deployment.

## Prerequisites

### On the Machine with Internet Access

1. **Conda Environment**: The internvl_env conda environment must be activated
2. **Git LFS**: Required for downloading large model files
3. **Sufficient Storage**: InternVL3-8B requires approximately 15-20GB of storage space
4. **Network Access**: Stable internet connection for downloading ~15GB of model files

### System Requirements

- **RAM**: Minimum 16GB, recommended 32GB+ for model loading
- **Storage**: At least 25GB free space (model files + temporary space)
- **GPU** (for inference): NVIDIA GPU with 12GB+ VRAM recommended

## Step-by-Step Download Process

### Step 1: Environment Setup

```bash
# Ensure you're in the project directory
cd /path/to/internvl_PoC

# Activate the conda environment
conda activate internvl_env

# Verify conda environment is active
echo $CONDA_PREFIX
# Should show path containing 'internvl_env'
```

### Step 2: Verify Prerequisites

```bash
# Check if git-lfs is installed
git lfs version

# If not installed, install it
conda install -c conda-forge git-lfs

# Initialize git-lfs (run once per system)
git lfs install
```

### Step 3: Download the Model

#### Option A: Download to Default Cache Location

```bash
python huggingface_model_download.py --model_name "OpenGVLab/InternVL3-8B"
```

This downloads to: `~/.cache/huggingface/models/OpenGVLab_InternVL3-8B/`

#### Option B: Download to Custom Directory (Recommended)

```bash
# Create a models directory
mkdir -p models

# Download to specific location
python huggingface_model_download.py \
    --model_name "OpenGVLab/InternVL3-8B" \
    --output_dir "models/InternVL3-8B"
```

### Step 4: Verify Download

```bash
# Check the downloaded files
ls -la models/InternVL3-8B/

# Expected files should include:
# - config.json
# - configuration_internvl_chat.py  
# - modeling_internvl_chat.py
# - preprocessor_config.json
# - tokenizer.json
# - tokenizer_config.json
# - pytorch_model*.bin or model*.safetensors files
# - README.md
```

### Step 5: Test Model Loading (Optional)

```bash
# Test if the model can be loaded (this will use significant RAM)
python -c "
from transformers import AutoModel, AutoTokenizer
model_path = 'models/InternVL3-8B'
print('Loading tokenizer...')
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)
print('Tokenizer loaded successfully')
print('Loading model...')
model = AutoModel.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)
print('Model loaded successfully')
print(f'Model config: {model.config}')
"
```

## Transferring Model to Remote Machine

### Step 1: Create Archive

```bash
# Create compressed archive of the model
tar -czf InternVL3-8B.tar.gz -C models InternVL3-8B/

# Check archive size
ls -lh InternVL3-8B.tar.gz
```

### Step 2: Transfer Methods

#### Option A: SCP Transfer
```bash
# Transfer to remote machine
scp InternVL3-8B.tar.gz user@remote-machine:/path/to/destination/

# On remote machine, extract
ssh user@remote-machine
cd /path/to/destination/
tar -xzf InternVL3-8B.tar.gz
```

#### Option B: rsync Transfer
```bash
# More robust for large files
rsync -avz --progress models/InternVL3-8B/ user@remote-machine:/path/to/models/InternVL3-8B/
```

#### Option C: USB/External Drive
```bash
# Copy to external drive
cp -r models/InternVL3-8B /media/external-drive/

# On remote machine
cp -r /media/external-drive/InternVL3-8B /path/to/models/
```

## Configuration for Offline Use

### Step 1: Update Environment Variables

On the remote machine, create or update `.env` file:

```bash
# Model path - use absolute path to downloaded model
INTERNVL_MODEL_PATH=/path/to/models/InternVL3-8B

# Other required paths
INTERNVL_PROJECT_ROOT=/path/to/internvl_PoC
INTERNVL_DATA_PATH=data
INTERNVL_OUTPUT_PATH=output
INTERNVL_SOURCE_PATH=src
INTERNVL_PROMPTS_PATH=prompts.yaml
INTERNVL_PROMPT_NAME=australian_optimized_prompt
```

### Step 2: Verify Offline Model Loading

```bash
# Load environment variables
source <(grep -v '^#' .env | sed 's/^/export /') > /dev/null 2>&1

# Test offline model loading
python -c "
import os
from src.internvl.model.loader import load_model_and_tokenizer

model_path = os.environ.get('INTERNVL_MODEL_PATH')
print(f'Loading model from: {model_path}')

try:
    model, tokenizer = load_model_and_tokenizer(
        model_path=model_path,
        device='cpu',  # Use CPU for testing
        local_files_only=True
    )
    print('✅ Model loaded successfully in offline mode')
    print(f'Model type: {type(model)}')
    print(f'Tokenizer type: {type(tokenizer)}')
except Exception as e:
    print(f'❌ Error loading model: {e}')
"
```

## Testing the Complete Pipeline

### Step 1: Single Image Test

```bash
# Test with a single image
python -m src.scripts.internvl_single \
    --image-path test_receipt.png \
    --verbose
```

### Step 2: Batch Processing Test

```bash
# Test batch processing
python -m src.scripts.internvl_batch \
    --image-folder-path data/synthetic/images \
    --prompt-name australian_optimized_prompt
```

## Troubleshooting

### Common Issues

#### 1. Git LFS Not Installed
```bash
# Error: "git: 'lfs' is not a git command"
# Solution:
conda install -c conda-forge git-lfs
git lfs install
```

#### 2. Insufficient Disk Space
```bash
# Check available space
df -h

# Clean up if needed
conda clean --all
rm -rf ~/.cache/huggingface/transformers/  # Remove old cached models
```

#### 3. Download Interrupted
```bash
# Resume interrupted git clone
cd models/InternVL3-8B  # or wherever download was interrupted
git lfs pull  # Resume LFS file downloads
```

#### 4. Model Loading Errors on Remote Machine
```bash
# Verify all files transferred correctly
find models/InternVL3-8B -name "*.bin" -o -name "*.safetensors" | wc -l
# Should show multiple model weight files

# Check file permissions
chmod -R 755 models/InternVL3-8B/
```

#### 5. Memory Issues During Model Loading
```bash
# Use CPU-only mode for testing
export CUDA_VISIBLE_DEVICES=""

# Or limit GPU memory if using GPU
export CUDA_VISIBLE_DEVICES=0
```

## Security Considerations

### File Integrity Verification

```bash
# Create checksums before transfer
find models/InternVL3-8B -type f -exec sha256sum {} \; > model_checksums.txt

# On remote machine, verify integrity
sha256sum -c model_checksums.txt
```

### Network Security

- Use SSH keys for secure transfer
- Consider VPN for sensitive environments
- Verify model authenticity from HuggingFace

## Storage Optimization

### Disk Space Management

```bash
# Remove unnecessary files after successful transfer
rm -f InternVL3-8B.tar.gz  # Remove archive after extraction

# Use symbolic links if multiple projects need the same model
ln -s /shared/models/InternVL3-8B /project1/models/InternVL3-8B
ln -s /shared/models/InternVL3-8B /project2/models/InternVL3-8B
```

## Performance Considerations

### GPU Memory Requirements

- **InternVL3-8B**: Requires approximately 12-16GB VRAM for inference
- **CPU fallback**: Possible but significantly slower (minutes vs seconds per image)

### Batch Processing Optimization

```bash
# Adjust batch size based on available memory
export INTERNVL_MAX_WORKERS=2  # Reduce for memory constraints
export INTERNVL_IMAGE_SIZE=448  # Smaller images for faster processing
```

## Production Deployment Checklist

- [ ] Model successfully downloaded and verified
- [ ] All files transferred to remote machine
- [ ] Environment variables configured
- [ ] Offline model loading tested
- [ ] Single image processing tested
- [ ] Batch processing tested
- [ ] GPU/CPU configuration optimized
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented

## Support and Troubleshooting

If you encounter issues:

1. **Check logs**: Enable verbose logging with `--verbose` flag
2. **Verify environment**: Ensure conda environment is properly activated
3. **Check paths**: Verify all paths in `.env` file are correct
4. **Test connectivity**: Ensure model files are accessible
5. **Memory monitoring**: Watch RAM/GPU usage during model loading

## Model Information

- **Model Name**: OpenGVLab/InternVL3-8B
- **Model Size**: ~15GB
- **Architecture**: Vision-Language Transformer
- **Input**: Images + Text prompts
- **Output**: Text responses (JSON for structured extraction)
- **Optimal GPU**: 12GB+ VRAM (RTX 3080/4080, A100, etc.)
- **Minimum RAM**: 16GB system RAM recommended