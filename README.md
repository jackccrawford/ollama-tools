# Ollama Multi-GPU Docker Management Tools

A comprehensive suite of tools for managing multiple Ollama Docker containers across multiple GPUs.

## Overview

This toolset enables efficient management of multiple Ollama instances across multiple GPUs, allowing for:

- Parallel model execution across different GPUs
- GPU preference assignment for optimal resource utilization
- Shared model storage to minimize disk usage
- Seamless container upgrades while preserving configurations
- Advanced file reading and document processing capabilities
- API access for programmatic interactions

## Core Architecture

- **Multiple Containers**: 4 Ollama Docker containers (`git-ollama0-1` through `git-ollama3-1`)
- **Port Mapping**: Each container maps to a different port (11434-11437)
- **GPU Preferences**: Each container has a preferred GPU while maintaining access to all GPUs
- **Shared Models**: All containers share a common model storage directory
- **Environment Selection**: `OLLAMA_INSTANCE` environment variable (0-3) selects the target container

## Basic Usage

### Core Commands

```bash
# Set the instance (0-3) to target a specific container
export OLLAMA_INSTANCE=0  # Targets git-ollama0-1 on port 11434

# Run a model interactively
ollama run phi4

# Run a model with a specific prompt
ollama run phi4 "Write a poem about AI"

# List available models
ollama list

# Show running models on all instances
ollama-ps

# Stop a model on a specific instance
ollama-stop phi4

# Stop a model on all instances
ollama-stop-all phi4
```

## Script Reference

### Core Wrapper Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `ollama` | Main wrapper that forwards commands to the selected Docker container | `ollama [command]` |
| `ollama-run` | Run a model on a specific instance | `ollama-run [instance] [model] [prompt]` |
| `ollama-stop` | Stop a model on a specific instance | `ollama-stop [instance] [model]` |
| `ollama-stop-all` | Stop a model on all instances | `ollama-stop-all [model]` |
| `ollama-ps` | Show running models across all instances | `ollama-ps` |
| `ollama-run-all` | Run a model on one or all instances | `ollama-run-all [instance|all] [model] [prompt]` |

### API and Advanced Interaction

| Script | Description | Usage |
|--------|-------------|-------|
| `ollama-api` | Send prompts via HTTP API | `ollama-api [options] "prompt"` |
| `ollama-file-reader` | Chat with a model that can read files | `ollama-file-reader [options]` |
| `read-with-ollama` | Python wrapper for file reading | `read-with-ollama [options]` |
| `summarize-document` | Quick document summarization | `summarize-document [options] file_path` |
| `compare-models-reading` | Compare how different models interpret a file | `compare-models-reading [options] file_path` |

### Management Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `list-ollama-models.sh` | List available models on a port | `list-ollama-models.sh [port]` |
| `sort_ollama_models.sh` | Re-pull models to update timestamps | `sort_ollama_models.sh` |
| `upgrade-ollama-containers.sh` | Upgrade containers while preserving configs | `upgrade-ollama-containers.sh [options]` |
| `assign-ollama-gpu-preferences.sh` | Configure GPU preferences | `assign-ollama-gpu-preferences.sh [options]` |

## GPU Configuration

### Preferred GPU Assignment

Each container is configured with a preferred GPU order:

| Container | Port | Preferred GPU Order |
|-----------|------|---------------------|
| git-ollama0-1 | 11434 | 0,1,2,3 |
| git-ollama1-1 | 11435 | 1,0,2,3 |
| git-ollama2-1 | 11436 | 2,0,1,3 |
| git-ollama3-1 | 11437 | 3,0,1,2 |

This configuration:
- Makes each container prefer a different GPU initially
- Allows access to all GPUs if the preferred one is busy
- Optimizes for smaller models that fit on a single GPU
- Enables parallel execution across multiple GPUs

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OLLAMA_INSTANCE` | Selects which Docker container to target | `export OLLAMA_INSTANCE=0` |
| `OLLAMA_MODELS` | Points to shared model storage location | `/root/.ollama/models` |
| `OLLAMA_HOST` | Configures the server binding | `0.0.0.0:11434` |
| `CUDA_VISIBLE_DEVICES` | Sets GPU preference order | `0,1,2,3` |
| `NVIDIA_VISIBLE_DEVICES` | Controls which GPUs are visible | `all` |

## Advanced Features

### File Reading with Function Calling

Models with function calling capabilities can read and analyze files:

```bash
# Start an interactive session with file reading capabilities
ollama-file-reader -m llama3.1

# Summarize a document directly
summarize-document -f markdown /path/to/document.md

# Compare how different models interpret the same file
compare-models-reading /path/to/file.md
```

### API Access

Send prompts directly to the API:

```bash
# Basic API call
ollama-api "What is the capital of France?"

# Advanced API call with options
ollama-api -m mistral -i 1 -s "You are a helpful coding assistant" "How do I read a file in Python?"
```

## System Maintenance

### Upgrading Containers

```bash
# Check current configuration without upgrading
upgrade-ollama-containers.sh --check-only

# Verify Ollama versions without upgrading
upgrade-ollama-containers.sh --verify-only

# Upgrade all containers with confirmation
upgrade-ollama-containers.sh

# Force upgrade without confirmation
upgrade-ollama-containers.sh --force
```

### Managing GPU Preferences

```bash
# Check current GPU configuration
assign-ollama-gpu-preferences.sh --check-only

# Update GPU preferences with confirmation
assign-ollama-gpu-preferences.sh

# Force update without confirmation
assign-ollama-gpu-preferences.sh --force
```

## Supported Models

### Function Calling Models

For file reading and document processing:
- llama3.1
- mistral-nemo
- nemotron-mini
- llama3-groq-tool-use
- firefunction-v2
- command-r-plus

### General Models

Any model supported by Ollama can be used, including:
- phi4, phi4-mini
- r1-1776
- llama3.2-vision
- dolphin3
- mistral
- and many others

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure scripts are executable with `chmod +x ~/bin/script_name`
2. **Container Not Found**: Check if containers are running with `docker ps`
3. **Model Not Found**: Pull the model first with `ollama pull model_name`
4. **GPU Not Used**: Verify GPU preferences with `assign-ollama-gpu-preferences.sh --check-only`

### Verification Commands

```bash
# Check running containers
docker ps --filter "name=git-ollama"

# Check container GPU configuration
docker exec git-ollama0-1 env | grep -E "CUDA|NVIDIA"

# Verify model availability
OLLAMA_INSTANCE=0 ollama list

# Check GPU utilization
nvidia-smi
```

## Architecture Benefits

- **Process-Level Parallelism**: Run multiple models simultaneously across different GPUs
- **Resource Isolation**: Prevent resource contention by directing models to specific GPUs
- **Shared Model Storage**: Minimize disk usage by sharing models between containers
- **GPU Preference**: Optimize resource allocation while maintaining flexibility
- **Seamless Upgrades**: Update containers while preserving configurations and preferences

## Performance Considerations

- **PCIe Bandwidth**: The primary bottleneck is PCIe bus bandwidth between CPU and GPUs
- **Model Caching**: Ollama caches models in GPU memory (default 5 minutes, tunable)
- **GPU Memory**: Smaller models (<12GB) can run on a single GPU, larger models may need multiple GPUs
- **Container Overhead**: Minimal overhead from using Docker containers

## Further Documentation

For more detailed information, refer to the following documentation files:
- `README_OLLAMA.md`: Overview of scripts, usage, and models
- `ollama-gpu-assignments.md`: GPU assignment details
- `ollama-gpu-preferred-assignments.md`: Preferred GPU configuration
- `README_FILE_READER.md`: File reading utilities
- `ollama-docker-vs-standard.md`: Docker vs. standard Ollama comparison
- `ollama-upgrade-guide.md`: Container upgrade instructions
- `ollama-gpu-preferences-guide.md`: GPU preference configuration
