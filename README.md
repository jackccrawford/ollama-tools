# Ollama NVIDIA GPU Management Tools for the Agentic AI Community

[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-Multi--GPU-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![Ollama](https://img.shields.io/badge/Ollama-Multi--Container-4285F4?style=for-the-badge)](https://ollama.ai/)
[![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![GPU](https://img.shields.io/badge/GPU-Preference_Management-FF6F00?style=for-the-badge&logo=nvidia&logoColor=white)]()
[![Parallelism](https://img.shields.io/badge/Parallelism-Process--Level-22C55E?style=for-the-badge)]()
[![Status](https://img.shields.io/badge/Status-Production_Ready-EAB308?style=for-the-badge)]()
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Container-9ca3af?style=for-the-badge)]()
[![Resource](https://img.shields.io/badge/Resource-Optimization-ff69b4?style=for-the-badge)]()

## Multi-GPU Docker Management for Ollama

A comprehensive suite of tools for managing multiple Ollama Docker containers across multiple GPUs, enabling parallel model execution and optimized resource utilization.

## Overview

ollama-tools enables efficient management of multiple Ollama instances across multiple GPUs, allowing for:

- Parallel model execution across different GPUs
- GPU preference assignment for optimal resource utilization
- Shared model storage to minimize disk usage
- Seamless container upgrades while preserving configurations
- Advanced file reading and document processing capabilities
- API access for programmatic interactions

## 🚧 Project Status & Features

### ✅ Current Features
- Multi-container Docker management (4 containers on separate ports)
- **Remote host support** for distributed AI constellation architecture
- GPU preference assignment system
- Shared model storage across containers
- Interactive and prompt-based model execution
- File reading with function calling support
- API access for programmatic interactions
- Container upgrade with configuration preservation
- Document summarization and comparison
- **Meta-AI orchestration** - using Ollama to intelligently decide how to use Ollama

### 🚀 High-Priority TODOs

#### 1. Meta-AI Orchestration (NEW)
- [ ] Intelligent request routing: "Can we offload this to another instance?"
- [ ] Performance-aware model selection: "I need a response in 10 seconds, can you handle it?"
- [ ] Multi-step workflow automation with function calling
- [ ] Web search → digestion → memory persistence pipelines
- [ ] Self-assessing capability matching for optimal resource utilization

#### 2. Enhanced Monitoring
- [ ] Real-time GPU utilization tracking
- [ ] Container health monitoring
- [ ] Model usage statistics
- [ ] Performance metrics dashboard

#### 3. Advanced Resource Management
- [ ] Dynamic GPU assignment based on workload
- [ ] Automatic container scaling
- [ ] Memory optimization for large models
- [ ] Load balancing across containers

#### 4. Extended Functionality
- [ ] Multi-model pipeline support
- [ ] Batch processing capabilities
- [ ] Streaming response optimization
- [ ] Custom model fine-tuning integration

## Architecture: Multi-Container Multi-GPU Setup

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  git-ollama0-1  │    │  git-ollama1-1  │    │  git-ollama2-1  │    │  git-ollama3-1  │
│   (Port 11434)  │    │   (Port 11435)  │    │   (Port 11436)  │    │   (Port 11437)  │
│ Prefers GPU 0   │    │ Prefers GPU 1   │    │ Prefers GPU 2   │    │ Prefers GPU 3   │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │                      │
         ▼                      ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                             Shared Model Storage                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
         ▲                      ▲                      ▲                      ▲
         │                      │                      │                      │
┌────────┴────────┐    ┌────────┴────────┐    ┌────────┴────────┐    ┌────────┴────────┐
│      GPU 0      │    │      GPU 1      │    │      GPU 2      │    │      GPU 3      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### GPU Preference System

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
| `ollama-api` | Send prompts via HTTP API (supports remote hosts) | `ollama-api [options] "prompt"` |
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

Send prompts directly to the API with support for remote hosts:

```bash
# Basic API call (local)
ollama-api "What is the capital of France?"

# Remote API call to distributed infrastructure
ollama-api -r 192.168.0.224 -m gpt-oss:120b "Complex reasoning task"

# Advanced API call with options
ollama-api -m mistral -i 1 -s "You are a helpful coding assistant" "How do I read a file in Python?"
```

### Meta-AI Orchestration (Experimental)

Use AI models to intelligently decide how to use AI infrastructure:

```bash
# Performance-aware routing
ollama-api -m phi4 "I have a complex reasoning task that needs to complete in 30 seconds. Can you route this optimally?"

# Capability assessment
ollama-api "Can you analyze this dataset and determine if it should be processed locally or on the GPU cluster?"

# Multi-step workflow automation
ollama-api -m llama3.1 "Please: 1) search the web for recent AI papers, 2) digest the findings with web-digester-phi4:3b, 3) save results to memory using MCP"
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Jack C Crawford** - CEO and Co-Founder at https://mvara.ai

## Contact

Email: jack@mvara.ai
X: https://x.com/jackccrawford
GitHub: https://github.com/jackccrawford
