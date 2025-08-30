# Ollama Master MCP Server

## Meta-AI Orchestration for Ollama Infrastructure

The Ollama Master MCP Server is a revolutionary Model Context Protocol server that provides intelligent orchestration for multiple Ollama instances. It enables AI agents (like Claude) to automatically discover, route, and manage requests across your entire Ollama constellation.

## Features

### 🔍 Automatic Discovery
- Scans network for Ollama instances (ports 11434-11499)
- Detects both local and remote instances
- Maintains real-time availability status
- Discovers available models on each instance

### 🧠 Intelligent Routing
- Analyzes request complexity and requirements
- Selects optimal model based on task
- Routes to best instance based on:
  - Model availability
  - Instance load
  - GPU resources
  - Network locality

### ⚡ Performance Optimization
- Prefers local instances for small models
- Routes large models to GPU clusters
- Automatic failover on instance unavailability
- Load balancing across multiple instances

### 🔄 Self-Assessment
- Evaluates whether infrastructure can handle tasks
- Provides time estimates for completion
- Recommends optimal approach for each request

## Installation

```bash
# Navigate to the MCP server directory
cd mcp-servers/ollama-master

# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

## Configuration

Add to your Claude Desktop `settings.json`:

```json
{
  "mcpServers": {
    "ollama-master": {
      "command": "python",
      "args": ["/Users/mars/Dev/ollama-tools/mcp-servers/ollama-master/src/server.py"],
      "env": {}
    }
  }
}
```

## Available Tools

### discover_instances
Discovers all available Ollama instances on the network.

```
Returns:
- List of instances with host, port, models, and GPU count
- Distinguishes between local and remote instances
```

### route_request
Intelligently routes a request to the best available instance.

```
Parameters:
- prompt: The prompt to send
- model: (optional) Specific model to use
- performance: (optional) "fast", "balanced", or "powerful"
- max_time: (optional) Maximum response time in seconds

Returns:
- Response from the selected model
- Instance and model used
- Success/error status
```

### list_models
Lists all available models across all discovered instances.

```
Returns:
- Dictionary of models and their available instances
- Total unique model count
```

### assess_capability
Assesses whether the infrastructure can handle a specific task.

```
Parameters:
- task_description: Description of the task
- requirements: (optional) Specific requirements

Returns:
- Can handle: true/false
- Recommended approach
- Estimated completion time
```

## Usage Examples

### Simple Query Routing
```
User: "What is the capital of France?"
→ Master MCP selects: phi4 on local instance (fast response)
```

### Complex Task Routing
```
User: "Analyze this 50-page document and provide insights"
→ Master MCP selects: gpt-oss:20b on remote GPU cluster
```

### Multi-Model Comparison
```
User: "Compare how different models interpret this prompt"
→ Master MCP orchestrates: Parallel execution across multiple instances
```

### Capability Assessment
```
User: "Can you handle a real-time conversation with 100ms latency?"
→ Master MCP assesses: Recommends phi4 on local instance
```

## Architecture

```
Claude/AI Agent
      ↓
Ollama Master MCP
      ↓
┌─────────────────────────────┐
│   Discovery Engine          │
│   Capability Mapper         │
│   Request Router            │
│   Load Balancer            │
└─────────────────────────────┘
      ↓
Local Instances | Remote Instances
   (Mars)       |   (Explora)
```

## Model Capability Tiers

### Fast Tier (< 3GB)
- phi4, phi4-mini
- Best for: Quick responses, simple queries
- Target latency: < 5 seconds

### Balanced Tier (3-10GB)
- llama3.1:8b, mistral
- Best for: General conversation, analysis
- Target latency: 10-30 seconds

### Powerful Tier (> 10GB)
- gpt-oss:20b, codellama:33b
- Best for: Complex reasoning, code generation
- Target latency: 30-120 seconds

## Advanced Features

### Workflow Orchestration
The Master MCP can coordinate multi-step workflows:
1. Web search with one model
2. Digest results with another
3. Save to memory with MCP
4. Generate final response

### Self-Aware Infrastructure
The system can assess its own capabilities:
- "Can I handle this task?"
- "What's the best model for this?"
- "Should this run locally or remotely?"

### Dynamic Scaling
Automatically adapts to:
- New instances coming online
- Models being loaded/unloaded
- Network conditions changing
- GPU availability fluctuating

## Development

### Adding New Model Capabilities
Edit `server.py` and add to `_initialize_model_capabilities()`:

```python
self.model_capabilities["new_model"] = ModelCapability(
    name="new_model",
    size_gb=5.0,
    capabilities=["general", "specialized"],
    performance_tier="balanced",
    preferred_tasks=["specific_use_case"]
)
```

### Extending Discovery Range
Modify the discovery loop in `discover_instances()`:

```python
# Extended discovery for custom port range
for port in range(START_PORT, END_PORT):
    instance = await self._check_instance(host, port, name)
```

## Troubleshooting

### No instances discovered
- Check Ollama containers are running: `docker ps`
- Verify network connectivity
- Check firewall settings

### Model not found
- Ensure model is pulled: `ollama pull model_name`
- Verify model is available on target instance

### Slow responses
- Check GPU utilization: `nvidia-smi`
- Monitor instance load
- Consider model size vs available resources

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Historical performance tracking
- [ ] Automatic model pulling on demand
- [ ] Cost optimization for cloud instances
- [ ] Multi-region support
- [ ] Custom routing policies
- [ ] A/B testing for model selection
- [ ] Conversation context management

## License

MIT - See LICENSE file for details

## Author

Built as part of the Ollama Tools suite for the Agentic AI Community