# Ollama Docker Container Upgrade Guide

This guide provides instructions for upgrading Ollama in Docker containers while preserving configurations and ensuring models point to a shared directory.

## Overview

The upgrade process involves:
1. Checking the current configuration of Ollama containers
2. Pulling the latest Ollama image
3. Upgrading each container while preserving its configuration
4. Verifying the upgrade was successful

## Using the Upgrade Script

A script has been created to automate the upgrade process: `~/bin/upgrade-ollama-containers.sh`

### Making the Script Executable

Before using the script, make it executable:

```bash
chmod +x ~/bin/upgrade-ollama-containers.sh
```

### Script Options

The script supports several options:

- `--help` or `-h`: Display help message
- `--check-only` or `-c`: Check current configuration without upgrading
- `--verify-only` or `-v`: Verify Ollama versions without upgrading
- `--force` or `-f`: Force upgrade without confirmation

### Example Usage

1. Check current configuration without upgrading:
   ```bash
   ~/bin/upgrade-ollama-containers.sh --check-only
   ```

2. Verify current Ollama versions:
   ```bash
   ~/bin/upgrade-ollama-containers.sh --verify-only
   ```

3. Interactive upgrade with confirmation:
   ```bash
   ~/bin/upgrade-ollama-containers.sh
   ```

4. Force upgrade without confirmation:
   ```bash
   ~/bin/upgrade-ollama-containers.sh --force
   ```

## Manual Upgrade Process

If you prefer to upgrade manually, follow these steps:

### 1. Check Current Configuration

```bash
# List running containers
docker ps | grep ollama

# Inspect container configuration
docker inspect <container-name>
```

### 2. Pull the Latest Ollama Image

```bash
docker pull ollama/ollama:latest
```

### 3. Upgrade Each Container

For each container:

```bash
# Stop the container
docker stop <container-name>

# Remove the container (this preserves the volume data)
docker rm <container-name>

# Recreate the container with ultra-high performance configuration
docker run -d \
  --name <container-name> \
  --restart always \
  --runtime=nvidia \
  --shm-size=32g \
  --memory=100g \
  --cpus="10" \
  --ulimit memlock=-1 \
  --ulimit stack=268435456 \
  --ulimit nofile=1048576 \
  -v <config-volume>:/root/.ollama \
  -v <shared-models-path>:/root/.ollama/models \
  -p <host-port>:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e CUDA_VISIBLE_DEVICES=<gpu-order> \
  -e OLLAMA_NUM_PARALLEL=3 \
  -e OLLAMA_MAX_LOADED_MODELS=12 \
  -e OLLAMA_FLASH_ATTENTION=1 \
  -e OLLAMA_KV_CACHE_TYPE=f16 \
  -e OLLAMA_KEEP_ALIVE=24h \
  -e OMP_NUM_THREADS=8 \
  -e CUDA_CACHE_MAXSIZE=4294967296 \
  -e OLLAMA_LOAD_TIMEOUT=600 \
  -e OLLAMA_REQUEST_TIMEOUT=300 \
  --gpus all \
  ollama/ollama:latest
```

### 4. Verify the Upgrade

```bash
# Check container is running
docker ps | grep <container-name>

# Verify Ollama version
docker exec <container-name> ollama --version

# Check models are accessible
docker exec <container-name> ollama list
```

## Current Setup Details

Your current setup consists of four Ollama containers with the following configuration:

- Container names: git-ollama0-1, git-ollama1-1, git-ollama2-1, git-ollama3-1
- Each container has its own Docker volume for configuration (git_ollama0_data, etc.)
- All containers share a common models directory from the host: /home/explora/.ollama/models
- Containers are exposed on ports 11434, 11435, 11436, and 11437
- All containers use `--runtime=nvidia` for optimal performance and GPU monitoring
- GPU preferences are configured via `CUDA_VISIBLE_DEVICES` environment variables
- Full GPU process visibility enabled for load balancing and orchestration

## Troubleshooting

If you encounter issues during the upgrade process:

1. **Container fails to start**: Check Docker logs with `docker logs <container-name>`
2. **Models not accessible**: Verify the shared models path is correctly mounted
3. **Version mismatch**: Ensure you pulled the latest image before creating new containers
4. **GPU not available**: Check that `--gpus all` is included in the run command

## Notes

- This process preserves all container configurations and ensures models continue to point to the shared directory
- The upgrade does not affect any models or their data
- Each container maintains its own configuration in its Docker volume
- All containers share the same models directory, preventing duplication
