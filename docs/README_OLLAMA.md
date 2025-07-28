# Ollama Utility Scripts

This collection of scripts provides a streamlined interface for working with Ollama large language models in a multi-instance Docker environment. These utilities make it easy to run, manage, and interact with various AI models locally.

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

As of the last update, the following models are available:
- granite3.2
- phi4 / phi4-mini
- r1-1776
- openthinker
- dolphin3
- llama3.2-vision
- nemotron-mini
- smollm2 (1.7b, 360m, 135m variants)
- mistral-nemo
- deepseek-r1:14b
- llama3:8b
- stablelm-zephyr:3b
- phi:2.7b
- neural-chat:7b
- qwen2.5-coder:32b
- codellama:7b
- mistral:7b

Use `ollama list` to see the complete current list of available models.

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

## Troubleshooting

- If you get "null" responses, the model may not be loaded. Start it first with `ollama-run`.
- If a port is busy, check if an instance is already running on that port with `ollama-ps`.
- For more detailed logs, examine Docker container logs: `docker logs git-ollama0-1`
