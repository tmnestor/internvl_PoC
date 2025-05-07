# Running InternVL on Shared Compute Resources

This guide provides best practices for running InternVL on shared compute resources like JupyterHub, HPC systems, or multi-user Linux servers.

## 1. Environment Isolation

### User-Specific Conda Environment

```bash
# Create a user-specific conda directory
mkdir -p ~/conda_envs

# Configure conda to recognize this directory
conda config --append envs_dirs ~/conda_envs

# Create the environment in your user space
conda env create -f internvl_env.yml --prefix ~/conda_envs/internvl_env

# Activate the environment
conda activate ~/conda_envs/internvl_env

# Verify the environment is active and properly configured
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Environment Variables

Create a user-specific `.env` file that includes absolute paths to your user directories:

```bash
cp .env.example .env
nano .env  # or your preferred text editor
```

Example `.env` file for a shared system:
```
INTERNVL_PATH=/home/your_username/path/to/internvl_PoC
INTERNVL_DATA_PATH=/home/your_username/path/to/internvl_PoC/data
INTERNVL_OUTPUT_PATH=/home/your_username/path/to/internvl_PoC/output
INTERNVL_MODEL_PATH=/shared/models/huggingface/hub/InternVL2_5-1B
INTERNVL_PROMPTS_PATH=/home/your_username/path/to/internvl_PoC/prompts.yaml
INTERNVL_IMAGE_FOLDER_PATH=/home/your_username/path/to/internvl_PoC/data/synthetic/images
```

## 2. GPU Resource Management

### Checking GPU Availability

```bash
# Check what GPUs are available and their usage
nvidia-smi
```

### Limiting GPU Usage

```bash
# Limit to specific GPUs (comma-separated)
export CUDA_VISIBLE_DEVICES=0,1

# Or limit to a single GPU
export CUDA_VISIBLE_DEVICES=0

# Check that the limitation worked
python -c "import torch; print(f'Number of available GPUs: {torch.cuda.device_count()}')"
```

### Memory Considerations

If sharing GPUs with others, consider setting memory limits:

```bash
# For TensorFlow (if used):
export TF_MEMORY_ALLOCATION="0.7"  # Use only 70% of available GPU memory

# For PyTorch, you can limit in code:
python -c "import torch; torch.cuda.set_per_process_memory_fraction(0.7)"
```

## 3. Running Long Jobs

### Using tmux or screen

For long-running jobs, use tmux or screen to maintain sessions:

```bash
# Start a new tmux session
tmux new -s internvl_session

# Then run your command inside the session
./run.sh --remote batch --image-folder-path /path/to/images

# Detach from the session: Ctrl+B followed by D
# Reattach later with:
tmux attach -t internvl_session
```

### Using nohup

Alternatively, use nohup to run jobs that continue after logout:

```bash
# Run a job with output logged to a file
nohup ./run.sh --remote batch --image-folder-path /path/to/images > batch_log.txt 2>&1 &

# Check job status
tail -f batch_log.txt
```

### Using Job Schedulers

If your system has SLURM or another job scheduler:

```bash
# Create a submission script (internvl_job.sh)
cat > internvl_job.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=internvl
#SBATCH --output=internvl_%j.out
#SBATCH --error=internvl_%j.err
#SBATCH --time=24:00:00
#SBATCH --gres=gpu:1

# Load modules if needed
# module load anaconda/...

# Activate environment
source ~/.bashrc
conda activate ~/conda_envs/internvl_env

# Run the job
cd /home/your_username/path/to/internvl_PoC
./run.sh --remote batch --image-folder-path /path/to/images
EOF

# Submit the job
sbatch internvl_job.sh
```

## 4. SROIE Dataset Evaluation on Shared Resources

To run the SROIE evaluation on a shared system:

1. Edit the evaluation script for remote execution:

```bash
# Edit the script
nano evaluate_sroie.sh

# Change this line to use remote mode
MODE="--remote"

# Make sure all paths are absolute and use your user directory
```

2. Run the evaluation:

```bash
# Option 1: Direct execution
./evaluate_sroie.sh

# Option 2: Run in tmux
tmux new -s sroie_eval
./evaluate_sroie.sh
# Detach with Ctrl+B then D

# Option 3: Run with nohup
nohup ./evaluate_sroie.sh > sroie_eval.log 2>&1 &
```

## 5. Best Practices for Shared Systems

1. **Be mindful of storage usage**: Clean up temporary files regularly.

2. **Coordinate GPU usage**: Check who else is using GPUs before starting intensive tasks.

3. **Use relative paths in your code**: But absolute paths in your `.env` file.

4. **Set up environment detection**: Modify your scripts to detect whether you're running on your development machine or the shared system.

5. **Document your setup**: Keep notes on your environment configuration to make reproduction easier.

6. **Monitor resource usage**: Use tools like `htop`, `nvidia-smi`, and `du` to keep track of your resource consumption.

7. **Use the `--remote` flag**: Always use `./run.sh --remote` when running on shared systems to ensure proper path overrides.