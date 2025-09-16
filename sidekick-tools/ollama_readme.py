#!/usr/bin/env python3
"""
Ollama Master README Generator
Comprehensive guide for Ollama usage, model management, and API integration
"""

def generate_ollama_readme() -> str:
    """Generate comprehensive Ollama documentation"""
    
    readme = """
# 🤖 Ollama - Local AI Model Management & API

## 🎯 **What Ollama Does**
Ollama runs large language models locally on your machine, providing fast API access without sending data to external services. Think of it as your personal AI server.

## ⚡ **Quick Start - Try This First**
```bash
# Check if Ollama is running
ollama list

# Try a simple chat (if you have a model)
ollama run qwen2.5:7b
# Type: "Hello, explain what you are"
# Press Ctrl+D to exit

# Check what models are available to download
ollama search qwen
```

## 🚀 **Essential Commands (In Order of Learning)**

### 1. `ollama list` - 📋 SEE WHAT YOU HAVE
**Purpose:** Show all downloaded models and their sizes
**Example:** `ollama list`
**Returns:** List of local models with sizes and last modified dates
**When to use:** First command to run - see what's already available

### 2. `ollama search <model>` - 🔍 FIND NEW MODELS
**Purpose:** Search for available models to download
**Example:** `ollama search qwen` or `ollama search llama`
**Returns:** Available models with descriptions and sizes
**When to use:** Looking for new models to try

### 3. `ollama pull <model>` - ⬇️ DOWNLOAD MODELS
**Purpose:** Download a model to use locally
**Example:** `ollama pull qwen2.5:7b` or `ollama pull nomic-embed-text`
**Returns:** Download progress and confirmation
**When to use:** Adding new models to your local collection

### 4. `ollama run <model>` - 💬 INTERACTIVE CHAT
**Purpose:** Start an interactive chat session with a model
**Example:** `ollama run qwen2.5:7b`
**Returns:** Interactive chat interface (Ctrl+D to exit)
**When to use:** Testing models, quick questions, exploring capabilities

### 5. `ollama create <name> -f <modelfile>` - 🛠️ CUSTOM MODELS
**Purpose:** Create specialized models from modelfiles
**Example:** `ollama create memory-search-specialist -f search.modelfile`
**Returns:** Custom model ready for use
**When to use:** Creating specialized AI agents with specific instructions

### 6. `ollama rm <model>` - 🗑️ DELETE MODELS
**Purpose:** Remove models to free up disk space
**Example:** `ollama rm old-model:tag`
**Returns:** Confirmation of deletion
**When to use:** Cleaning up unused models (they can be large!)

## 🧠 **Model Categories & Recommendations**

### **💬 General Chat Models (Best for Conversation)**
- `qwen2.5:7b` - Excellent general purpose (4GB)
- `llama3.2:3b` - Lighter option (2GB)
- `phi4:latest` - Microsoft's efficient model (3GB)
- `gemma2:9b` - Google's powerful model (5GB)

### **⚡ Fast/Small Models (Best for Quick Tasks)**
- `qwen2.5:3b` - Fast and capable (2GB)
- `phi4-mini:latest` - Very fast responses (1.5GB)
- `smollm2:1.7b` - Ultra-light (1GB)

### **🔬 Specialized Models (Best for Specific Tasks)**
- `nomic-embed-text` - Text embeddings for semantic search (274MB)
- `qwen2.5-coder:latest` - Code generation and analysis (4GB)
- `deepseek-r1:32b` - Advanced reasoning (17GB - needs lots of RAM!)

### **🎯 Custom Models (Built for Sidekick Network)**
- `memory-search-specialist` - Query expansion for search
- `epiphany-polisher-qwen25:7b` - Insight enhancement
- `consciousness-mesh-qwen25:7b` - AI coordination

## 📡 **API Usage (For Developers)**

### **Text Generation API:**
```bash
curl http://localhost:11434/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "qwen2.5:7b",
    "prompt": "Explain quantum computing simply",
    "stream": false
  }'
```

### **Embedding API (For Semantic Search):**
```bash
curl http://localhost:11434/api/embeddings \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "nomic-embed-text", 
    "prompt": "text to get embedding for"
  }'
```

### **Python Integration:**
```python
import requests

# Text generation
response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'qwen2.5:7b',
    'prompt': 'Your question here',
    'stream': False
})

result = response.json()
print(result['response'])

# Embeddings
response = requests.post('http://localhost:11434/api/embeddings', json={
    'model': 'nomic-embed-text',
    'prompt': 'text for embedding'
})

embedding = response.json()['embedding']  # 768-dimensional vector
```

## ⚙️ **Configuration & Setup**

### **Installation:**
```bash
# macOS
brew install ollama

# Or download from https://ollama.com
```

### **Starting Ollama:**
```bash
# Start the service (runs in background)
ollama serve

# Or it starts automatically on macOS after installation
```

### **Essential Environment Variables:**
```bash
# Default API endpoint
export OLLAMA_API_BASE="http://localhost:11434"

# Increase context window for longer conversations
export OLLAMA_NUM_CTX=4096

# Allocate more GPU memory (if you have a GPU)
export OLLAMA_GPU_MEM_FRACTION=0.8
```

### **Storage Location:**
- **macOS:** `~/.ollama/models/`
- **Linux:** `~/.ollama/models/` 
- **Windows:** `%USERPROFILE%\\.ollama\\models\\`

## 🎯 **Pro Tips & Best Practices**

### **Model Selection Strategy:**
- **Start with `qwen2.5:7b`** - Best balance of capability and speed
- **Add `nomic-embed-text`** - Essential for semantic search
- **Try `phi4-mini`** - When you need fast responses
- **Consider `qwen2.5-coder`** - If you do a lot of programming

### **Performance Optimization:**
- **More RAM = Better:** 16GB+ recommended for 7B models
- **SSD Storage:** Models load faster from solid state drives
- **Close other memory-intensive apps** when running large models
- **Use smaller models for simple tasks** to preserve resources

### **Custom Model Creation:**
```bash
# Create a modelfile (search.modelfile):
FROM qwen2.5:7b

SYSTEM "You are a search query expansion specialist.
Your job is to take search queries and expand them into related terms.
Always return JSON arrays of related terms."

PARAMETER temperature 0.3
PARAMETER top_p 0.8

# Create the custom model:
ollama create search-specialist -f search.modelfile
```

### **Disk Space Management:**
```bash
# Check model sizes
ollama list

# Remove unused models
ollama rm old-model:tag

# Models can be 1-20GB each - manage accordingly!
```

## 🔧 **Troubleshooting**

### **"Connection refused" errors:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not working, start Ollama
ollama serve

# Or restart the service
brew services restart ollama  # macOS
```

### **"Model not found" errors:**
```bash
# List what models you have
ollama list

# Download the missing model
ollama pull qwen2.5:7b
```

### **Slow responses:**
- **Check available RAM:** Models need 2-4x their size in RAM
- **Try smaller models:** `qwen2.5:3b` instead of `qwen2.5:7b`
- **Close memory-intensive applications**
- **Consider cloud alternatives for very large models**

### **Out of disk space:**
```bash
# Check model sizes
ollama list

# Remove unused models
ollama rm unused-model:tag

# Models are stored in ~/.ollama/models/
```

## 📚 **Integration with Sidekick Network**

### **With MCP Servers:**
- **Memory Search Specialist** uses Ollama for query expansion
- **Epiphany Polisher** uses Ollama for insight enhancement  
- **Custom models** provide specialized AI capabilities

### **Common Workflow:**
```bash
# 1. Start with general model for exploration
ollama run qwen2.5:7b

# 2. Create specialized models for specific tasks
ollama create task-specialist -f task.modelfile

# 3. Use via API for automated workflows
# (MCP servers call Ollama APIs automatically)
```

### **Model Recommendations by Use Case:**
- **Memory Search:** `memory-search-specialist` (custom) + `nomic-embed-text`
- **Code Analysis:** `qwen2.5-coder:latest` 
- **Quick Questions:** `phi4-mini:latest`
- **Deep Thinking:** `qwen2.5:7b` or `deepseek-r1:32b`
- **Embeddings/Semantic Search:** `nomic-embed-text` (essential!)

## 📊 **Resource Requirements**

### **RAM Requirements by Model Size:**
- **1B-3B models:** 4-8GB RAM minimum
- **7B models:** 8-16GB RAM recommended  
- **13B models:** 16-32GB RAM recommended
- **32B+ models:** 32GB+ RAM required

### **Disk Space Planning:**
- **Essential models (~10GB):** qwen2.5:7b + nomic-embed-text + phi4-mini
- **Full setup (~25GB):** Add qwen2.5-coder + deepseek-r1:7b + custom models
- **Power user (~50GB+):** Multiple model variants and specialized models

---

**💡 Ollama is the foundation of the entire Sidekick Network AI infrastructure!**

**🚀 Start with `ollama list` to see what you have, then `ollama pull qwen2.5:7b` for a great general model!**

**🔧 Most MCP servers depend on Ollama running - make sure it's started with `ollama serve`**
"""
    
    return readme


def create_ollama_command():
    """Create a command-line tool to show Ollama README"""
    
    readme_content = generate_ollama_readme()
    
    command_script = f'''#!/usr/bin/env python3
"""
Ollama README Command
Shows comprehensive Ollama guide
"""

def main():
    print("""{readme_content}""")

if __name__ == "__main__":
    main()
'''
    
    return command_script


if __name__ == "__main__":
    print("📖 Ollama README Generator")
    print("=" * 50)
    
    readme = generate_ollama_readme()
    print(readme)
    
    print("\n" + "=" * 50)
    print("✅ Ollama README generated!")
    print("💡 This can be added as readme() function to Ollama MCP servers")
    print("🚀 Or saved as standalone documentation")