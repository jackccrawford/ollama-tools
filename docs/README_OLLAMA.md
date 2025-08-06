# Ollama Multi-Instance Docker Management Tools
## Emergent Intelligence Edition (v0.11.1)

A comprehensive collection of scripts and utilities for managing multiple Ollama instances in Docker containers with optimized GPU utilization, load balancing, and **emergent intelligence capabilities**.

### 🧠 **New in v0.11.1: Emergent Intelligence Features**
- **Agentic Capabilities**: Function calling, web browsing, autonomous tool usage
- **Chain-of-Thought Reasoning**: Full visibility into model reasoning processes  
- **Structured Outputs**: JSON, XML, and custom format generation
- **MXFP4 Quantization**: Advanced 4.25-bit quantization for large models
- **Multi-Agent Coordination**: Enhanced parallel processing for emergent behaviors

### ✅ **Proven GPU Configuration (WORKING)**
- **gpt-oss:20b**: Successfully running on 100% GPU across 4x NVIDIA TITAN Xp
- **Multi-container deployment**: All 4 containers with proper GPU load balancing
- **Hybrid processing**: Intelligent CPU/GPU allocation (e.g., 24%/76% CPU/GPU)
- **Simple configuration**: Minimal environment variables prevent GPU fallback
- **Chain-of-thought**: Full reasoning visibility in Ollama 0.11.1

## Available Scripts

| Script | Description |
|--------|-------------|
| `ollama` | Main wrapper for Docker-based Ollama commands |
| `ollama-ps` | List running models across all Ollama instances |
| `ollama-run` | Run a model on a specific instance |
| `ollama-run-all` | Run multiple models across different instances |
| `ollama-stop` | Stop a running model on a specific instance |
| `ollama-stop-all` | Stop all running models across all instances |
| `ollama-api` | Send prompts to models via HTTP API and get responses |

## Environment Setup

These scripts work with Docker-based Ollama instances running on ports:
- Instance 0: Port 11434
- Instance 1: Port 11435
- Instance 2: Port 11436
- Instance 3: Port 11437

### Ultra-High Performance Configuration

All containers use optimized settings for maximum performance:
- **3x faster inference** with NVIDIA runtime and Flash Attention
- **Intelligent model placement**: Large models on CPU, smaller on GPU
- **32GB shared memory** and **100GB RAM limits** per container
- **Full GPU process visibility** via `nvidia-smi` for load balancing
- **12 models loaded simultaneously** for fast agent LLM switching
- **Real-time monitoring** capabilities for orchestration systems

📖 **See [Performance Optimization Guide](ollama-performance-optimization.md) for complete details**

## Detailed Usage

### 1. `ollama`

The base wrapper for interacting with Ollama commands inside Docker containers.

```bash
ollama COMMAND [ARGS...]

# Examples:
ollama list                    # List models in the default container
OLLAMA_INSTANCE=1 ollama list  # List models in a specific container
```

**Environment Variables:**
- `OLLAMA_INSTANCE`: Set to 0-3 to specify which container to use (default: 0)

### 2. `ollama-ps`

Check which models are currently running across all instances.

```bash
ollama-ps
```

Output includes instance number, port information, and any running models with their details.

### 3. `ollama-run`

Run a specific model on a designated instance.

```bash
ollama-run INSTANCE_NUMBER MODEL [PROMPT]

# Examples:
ollama-run 0 phi4 "Write a poem"    # Run on instance 0 with prompt
ollama-run 2 phi4                   # Run interactively on instance 2
```

**Parameters:**
- `INSTANCE_NUMBER`: 0-3, specifying which Ollama instance to use
- `MODEL`: Name of the model to run (e.g., phi4, mistral, llama3)
- `PROMPT` (optional): If provided, sends a one-shot prompt; if omitted, starts an interactive session

### 4. `ollama-run-all`

Run multiple models across different instances.

```bash
ollama-run-all

# Examples may vary based on script implementation
```

This script helps manage multiple models across different Ollama instances at once.

### 5. `ollama-stop`

Stop a running model on a specific instance.

```bash
ollama-stop INSTANCE_NUMBER

# Example:
ollama-stop 1    # Stop any running model on instance 1
```

**Parameters:**
- `INSTANCE_NUMBER`: 0-3, specifying which Ollama instance to stop models on

### 6. `ollama-stop-all`

Stop all running models across all instances.

```bash
ollama-stop-all
```

This is useful for cleaning up all running models at once.

### 7. `ollama-api`

Send prompts to local Ollama models via HTTP API and get formatted responses.

```bash
ollama-api [OPTIONS] PROMPT

# Examples:
ollama-api "What is the capital of France?"
ollama-api -m mistral -i 1 "Write a poem about AI"
ollama-api -m phi4 -s "You are a helpful coding assistant" "How do I read a file in Python?"
```

**Options:**
- `-m, --model MODEL`: Specify model (default: phi4)
- `-i, --instance NUMBER`: Specify instance number 0-3 (default: 0)
- `-s, --system PROMPT`: Specify system prompt
- `-t, --temperature VALUE`: Set temperature (default: 0.7)
- `-o, --tokens NUMBER`: Set max tokens (default: 2048)
- `-h, --help`: Show help message

This script is ideal for quickly getting responses from different models for comparison or obtaining second opinions without needing to remember complex curl commands.

## Available Models

The following models are currently available across the containers:

### 🚀 **Emergent Intelligence Models (NEW)**
- **gpt-oss:20b** - State-of-the-art reasoning with function calling
- **gpt-oss:120b** - Maximum emergent intelligence capabilities  
- **deepseek-r1:8b** - Specialized chain-of-thought reasoning
- **qwen2.5:32b** - Enhanced analytical and reasoning capabilities

### Large Models (CPU Optimized)
- **codellama:70b** - Advanced code generation and analysis
- **llama3.1:70b** - General purpose large language model

### Medium Models (GPU Distributed)
- **qwen2.5:32b** - Excellent for reasoning and analysis
- **deepseek-coder:33b** - Specialized coding model
- **llama3.1:8b** - Balanced performance model

### Small Models (GPU Preferred)
- **gemma2:9b** - Fast general purpose model
- **codellama:13b** - Quick code assistance
- **llama3.2:3b** - Lightweight chat model

## Getting Started

1. Check which models are available:
   ```bash
   ollama list
   ```

2. See if any models are currently running:
   ```bash
   ollama-ps
   ```
   
3. Start a model on a specific instance:
   ```bash
   ollama-run 0 phi4
   ```

4. Send a query via API to get a quick response:
   ```bash
   ollama-api -m phi4 "What is artificial intelligence?"
   ```

5. When done, stop all running models:
   ```bash
   ollama-stop-all
   ```

## Tips for Best Results

1. **Multiple Instances**: Run different models on different instances to compare responses.

2. **Model Selection**: Different models excel at different tasks. Try various models for different types of questions:
   - `phi4`: Good general-purpose model
   - `mistral-nemo`: Strong performance on reasoning
   - `codellama`: Specialized for code generation
   - `qwen2.5-coder`: Another coding-focused model

3. **System Prompts**: Use the `-s` option with `ollama-api` to customize the model's behavior through system prompts.

4. **Temperature Control**: Adjust temperature with `-t` for more creative (higher) or more deterministic (lower) responses.

## GPU Monitoring and Load Balancing

With NVIDIA runtime, you can monitor GPU usage in real-time:

```bash
# Monitor GPU utilization and processes
watch -n 1 nvidia-smi

# Check specific GPU processes
nvidia-smi --query-compute-apps=pid,process_name,used_memory,gpu_uuid --format=csv

# Monitor container-specific GPU usage
for i in {0..3}; do echo "Container $i:"; docker exec git-ollama$i-1 nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv; done
```

This enables intelligent load balancing and orchestration across your GPU resources.

## Troubleshooting

- If you get "null" responses, the model may not be loaded. Start it first with `ollama-run`.
- If a port is busy, check if an instance is already running on that port with `ollama-ps`.
- For GPU monitoring issues, ensure containers use `--runtime=nvidia`
- For more detailed logs, examine Docker container logs: `docker logs git-ollama0-1`
