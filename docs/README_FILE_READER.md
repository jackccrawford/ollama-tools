# Ollama File Reader

This utility enables AI models to read files and explore the file system using Ollama's function calling capabilities. With this tool, you can have a conversation with an AI model and ask it questions about files on your system.

## Quick Start

```bash
# Basic usage
ollama-file-reader

# Advanced usage with specific model
ollama-file-reader -m llama3-groq-tool-use -i 0
```

Once in the chat, try asking:
- "What does the file /path/to/your/file.txt contain?"
- "List the files in /path/to/your/directory"
- "Summarize /path/to/your/README.md"

## Supported Models

For function calling to work properly, use one of these models:

| Model | Size | Strengths |
|-------|------|-----------|
| llama3.1 | 8B | Good all-around performance |
| llama3-groq-tool-use | 8B | Specialized for tool usage |
| mistral-nemo | 7B | Strong reasoning capabilities |
| nemotron-mini | 4B | Small yet effective |
| firefunction-v2 | Varies | Focus on function calling |
| command-r-plus | Varies | Command interpretation |

## Available Scripts

| Script | Description |
|--------|-------------|
| `ollama-file-reader` | Main tool for AI-assisted file reading |
| `compare-models-reading` | Compare how different models read and interpret the same file |
| `summarize-document` | Quick document summarization with a specific model |

## Function Capabilities

This tool gives models the ability to:

1. **Read Files**: Access and analyze text content
2. **List Directories**: View file system structure
3. **Get File Information**: Examine metadata like size and permissions

## Installation

No additional installation is needed beyond Ollama itself. The scripts are already in your `~/.local/bin` directory.

For models not already in your system:

```bash
# Install a model to a specific instance
OLLAMA_INSTANCE=0 ollama pull llama3-groq-tool-use
OLLAMA_INSTANCE=1 ollama pull mistral-nemo
```

## Command Options

```
Usage: ollama-file-reader [OPTIONS]

Options:
  -m, --model MODEL       Specify model (default: llama3.1)
  -i, --instance NUMBER   Specify instance number 0-3 (default: 0)
  -s, --system PROMPT     Specify system prompt
  -t, --temperature VALUE Set temperature (default: 0.7)
  -o, --tokens NUMBER     Set max tokens (default: 2048)
  -h, --help              Show this help message
```

## Practical Examples

### Working with Code

```bash
# Analyze a code file
ollama-file-reader
> "Please explain how the script at /path/to/your/script.sh works"
> "What dependencies does /path/to/some/script.py have?"
```

### Document Analysis

```bash
# Summarize documentation
ollama-file-reader
> "Summarize the main points in /path/to/your/document.md"
> "What are the key takeaways from this document?"
```

### Using Multiple Instances

```bash
# Start different models on different instances
ollama-file-reader -m llama3.1 -i 0
# In another terminal
ollama-file-reader -m mistral-nemo -i 1
```

## Common Questions

**Q: How large of a file can the model read?**  
A: Files are limited to about 100KB to avoid memory issues.

**Q: Can the model write to files?**  
A: No, this tool provides read-only access for security.

**Q: Which model is best for code analysis?**  
A: Try llama3-groq-tool-use or mistral-nemo for code understanding.

**Q: How do I get more detailed analysis?**  
A: Ask follow-up questions! The model remembers the file content during your conversation.

## Tips for Best Results

1. **Use Full Paths**: Always specify complete file paths
2. **One File at a Time**: Focus on a single file per question for best results
3. **Ask for Specifics**: "What does this code do?" works better than "Tell me about this file"
4. **Follow-up Questions**: After reading a file, you can ask more specific questions about it
5. **Model Selection**: Different models have different strengths:
   - llama3.1: Best general purpose model
   - llama3-groq-tool-use: Excellent for tool interactions
   - mistral-nemo: Good for detailed analysis
   - nemotron-mini: Faster responses for simpler tasks

## Troubleshooting

- **Model Not Found**: Make sure you've pulled the model with `OLLAMA_INSTANCE=X ollama pull MODEL`
- **Permission Errors**: Check if you have read access to the requested files
- **Low Quality Responses**: Try a different model or adjust the temperature
- **Truncated Output**: For large files, try asking about specific sections

## Integration with Other Tools

You can pipe file paths from other commands:

```bash
find /path -name "*.md" | xargs -I{} echo "Summarize {}" | ollama-file-reader -m llama3-groq-tool-use
```

## Security Considerations

- Models only have read access to files you explicitly mention
- No execution permissions for running code
- Access is limited to your user permissions
