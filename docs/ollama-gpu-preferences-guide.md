# Ollama GPU Preferences Configuration Guide

This guide explains how to configure Ollama Docker containers with preferred GPU assignments, which helps optimize GPU utilization and prevents blocking for small model footprints.

## Overview

The configuration assigns each Ollama container a preferred GPU while still allowing access to all GPUs if needed. This approach:

1. Distributes small models (under 12GB) across different GPUs
2. Prevents resource contention for typical workloads
3. Maintains flexibility for larger models to span multiple GPUs

## Configuration Scripts

Two scripts have been created to manage this configuration:

1. `~/bin/assign-ollama-gpu-preferences.sh`: Updates existing containers with GPU preferences
2. `~/bin/restore-ollama-containers.sh`: Recreates containers with GPU preferences and includes verification

### Making the Scripts Executable

Before using the scripts, make them executable:

```bash
chmod +x ~/bin/assign-ollama-gpu-preferences.sh
chmod +x ~/bin/restore-ollama-containers.sh
```

### Script Options

The assign-ollama-gpu-preferences.sh script supports several options:

- `--help` or `-h`: Display help message
- `--check-only` or `-c`: Check current configuration without updating
- `--force` or `-f`: Force update without confirmation

### Example Usage

1. Check current configuration without updating:
   ```bash
   ~/bin/assign-ollama-gpu-preferences.sh --check-only
   ```

2. Interactive update with confirmation:
   ```bash
   ~/bin/assign-ollama-gpu-preferences.sh
   ```

3. Force update without confirmation:
   ```bash
   ~/bin/assign-ollama-gpu-preferences.sh --force
   ```

4. Restore and verify containers:
   ```bash
   ~/bin/restore-ollama-containers.sh
   ```

## GPU Preference Configuration

The scripts configure the following GPU preferences:

| Container      | Preferred GPU | GPU Order     | Environment Variable           |
|----------------|---------------|---------------|--------------------------------|
| git-ollama0-1  | GPU 0         | 0,1,2,3       | CUDA_VISIBLE_DEVICES=0,1,2,3   |
| git-ollama1-1  | GPU 1         | 1,0,2,3       | CUDA_VISIBLE_DEVICES=1,0,2,3   |
| git-ollama2-1  | GPU 2         | 2,0,1,3       | CUDA_VISIBLE_DEVICES=2,0,1,3   |
| git-ollama3-1  | GPU 3         | 3,0,1,2       | CUDA_VISIBLE_DEVICES=3,0,1,2   |

Each container will:
1. First try to use its preferred GPU
2. If more memory is needed, use additional GPUs in the specified order
3. Maintain access to all GPUs through `NVIDIA_VISIBLE_DEVICES=all`

## How It Works

The configuration uses two key environment variables:

1. `NVIDIA_VISIBLE_DEVICES=all`: Makes all GPUs accessible to the container
2. `CUDA_VISIBLE_DEVICES=X,Y,Z`: Sets the preferred order of GPUs

When an Ollama container loads a model:
- It will first try to use the first GPU in the CUDA_VISIBLE_DEVICES list
- If that GPU doesn't have enough memory, it will try the next one in the list
- This continues until it finds enough GPU memory or falls back to CPU

## Verifying the Configuration

The restore-ollama-containers.sh script includes a verification function that:

1. Loads a small model (phi:2.7b) in each container
2. Shows detailed GPU usage information
3. Displays which GPU is being used by each container

This provides concrete proof that each container is using its preferred GPU.

You can also manually verify the GPU preferences with:

```bash
for i in {0..3}; do 
  echo "===== CONTAINER git-ollama$i-1 ====="; 
  docker exec git-ollama$i-1 env | grep CUDA; 
  echo; 
done
```

## Testing the Configuration

After applying the configuration, you can test it by:

1. Loading a small model in each container:
   ```bash
   docker exec git-ollama0-1 ollama run phi:2.7b "Hello world"
   docker exec git-ollama1-1 ollama run phi:2.7b "Hello world"
   docker exec git-ollama2-1 ollama run phi:2.7b "Hello world"
   docker exec git-ollama3-1 ollama run phi:2.7b "Hello world"
   ```

2. Checking GPU utilization:
   ```bash
   nvidia-smi
   ```

You should see each model loaded on its preferred GPU.

## Updating the Upgrade Script

To ensure these GPU preferences are preserved during future Ollama upgrades, you should update the upgrade script (`~/bin/upgrade-ollama-containers.sh`). The following changes are needed:

1. Add code to detect and preserve CUDA_VISIBLE_DEVICES settings
2. Include the environment variable when recreating containers

## Propagating to Other Machines

If you want to propagate this configuration to other machines:

1. Copy both scripts (`assign-ollama-gpu-preferences.sh` and `restore-ollama-containers.sh`)
2. Adjust the GPU preferences based on the number of GPUs available on each machine
3. Run the script on each machine to apply the configuration

For machines with fewer than 4 GPUs, you'll need to modify the script to assign preferences appropriately.

## Benefits of This Configuration

This configuration provides several advantages:

1. **Optimized Resource Distribution**: Each container has a preferred GPU, preventing resource contention
2. **Improved Performance**: Small models won't compete for the same GPU
3. **Flexibility for Large Models**: Larger models can still span multiple GPUs
4. **Graceful Fallback**: If preferred GPUs are full, processing can use other GPUs or fall back to CPU
5. **Consistent Behavior**: Each container will consistently try its preferred GPU first
