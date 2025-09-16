#!/usr/bin/env python3
"""
MCP README Template Generator
Creates comprehensive documentation for any MCP server
"""

def generate_mcp_readme(server_name: str, server_description: str, commands: list, config: dict = None) -> str:
    """Generate a comprehensive README for an MCP server
    
    Args:
        server_name: Name of the MCP server
        server_description: What this server does
        commands: List of command dictionaries with name, purpose, example, when_to_use
        config: Configuration requirements and setup
    
    Returns:
        Complete README content
    """
    
    readme = f"""
# 🔧 {server_name} MCP Server

## 🎯 **What This Server Does**
{server_description}

## ⚡ **Quick Start - Try This First**
```bash
# Always start with the README
readme

# Then try the most common command:
{commands[0]['example'] if commands else 'command_example'}
```

## 🚀 **Available Commands (In Order of Typical Use)**

"""
    
    # Add commands documentation
    for i, cmd in enumerate(commands, 1):
        readme += f"""### {i}. `{cmd['name']}` - {cmd.get('emoji', '🔧')} {cmd.get('priority', 'COMMAND')}
**Purpose:** {cmd['purpose']}
**Example:** `{cmd['example']}`
**Returns:** {cmd.get('returns', 'Command results')}
**When to use:** {cmd['when_to_use']}

"""
    
    # Add configuration section if provided
    if config:
        readme += """## ⚙️ **Configuration & Setup**

### **Required Environment Variables:**
```bash
"""
        for var, desc in config.get('required', {}).items():
            readme += f'export {var}="{desc}"\n'
        
        readme += "```\n"
        
        if config.get('optional'):
            readme += "\n### **Optional Configuration:**\n```bash\n"
            for var, desc in config.get('optional', {}).items():
                readme += f'export {var}="{desc}"\n'
            readme += "```\n"
        
        if config.get('prerequisites'):
            readme += "\n### **What You Need:**\n"
            for req in config['prerequisites']:
                readme += f"- {req}\n"
    
    readme += """
## 🎯 **Pro Tips**

### **Getting Better Results:**
- **Always start with `readme`** to understand the server
- **Follow the command order** - they're arranged by typical workflow
- **Check error messages** - they often contain helpful guidance

### **Integration with Other MCPs:**
- Use `search_status` or similar to check system health
- Combine results with other MCP servers for comprehensive workflows
- Save important discoveries with `memorize` from Memory Maker

---

**💡 Run `readme` anytime to see this guide again!**

**🚀 Start with the first command in the list above for the best experience!**
"""
    
    return readme


def create_readme_function(server_name: str, server_description: str, commands: list, config: dict = None) -> str:
    """Generate the actual readme() function code for an MCP server"""
    
    readme_content = generate_mcp_readme(server_name, server_description, commands, config)
    
    function_code = f'''@mcp.tool()
def readme() -> str:
    """📖 {server_name} - Complete Guide and Documentation
    
    Returns:
        Comprehensive guide with examples, workflows, and getting started info
    """
    
    guide = """{readme_content}"""
    
    return guide'''
    
    return function_code


# Example usage for different MCP servers
MEMORY_MAKER_CONFIG = {
    "server_name": "Memory Maker",
    "server_description": "Create, store, and retrieve structured memories with threading and actor management",
    "commands": [
        {
            "name": "memorize(data, parent_uuid?)",
            "emoji": "🧠",
            "priority": "START HERE", 
            "purpose": "Create structured memory with rich metadata",
            "example": 'memorize({"type": "insight", "content": "AI coordination patterns"}, "parent-uuid")',
            "returns": "Memory UUID and confirmation",
            "when_to_use": "Storing important insights, discoveries, or structured data"
        },
        {
            "name": "save(content, parent_uuid?)",
            "emoji": "💾", 
            "priority": "SIMPLE SAVE",
            "purpose": "Quickly save text content as a memory",
            "example": 'save("Important discovery about memory search", "parent-uuid")',
            "returns": "Memory UUID and confirmation", 
            "when_to_use": "Quick notes or simple text you want to remember"
        },
        {
            "name": "remember(query?, actor_uuid?)",
            "emoji": "🔍",
            "priority": "SEARCH MEMORIES",
            "purpose": "Search and retrieve memories by content or actor",
            "example": 'remember("AI coordination", "*")',
            "returns": "List of matching memories with metadata",
            "when_to_use": "Finding previously stored information"
        }
    ],
    "config": {
        "required": {
            "MEMORY_MAKER_DATABASE_PATH": "/path/to/database.db",
            "MEMORY_MAKER_ACTOR_UUID": "your-actor-uuid"
        },
        "prerequisites": [
            "✅ **SQLite database** for memory storage",
            "✅ **Actor UUID** for identity management", 
            "⭐ **Threading support** for conversation-like memory chains"
        ]
    }
}

EPIPHANY_POLISHER_CONFIG = {
    "server_name": "Epiphany Polisher", 
    "server_description": "Transform raw insights into articulated breakthroughs using cognitive enhancement AI",
    "commands": [
        {
            "name": "polish_insight(raw_insight, context?)",
            "emoji": "✨",
            "priority": "START HERE",
            "purpose": "Transform rough ideas into polished insights", 
            "example": 'polish_insight("memory search could be better with LLM expansion", "search optimization")',
            "returns": "Enhanced insight with deeper analysis",
            "when_to_use": "When you have a rough idea that needs clarity and depth"
        },
        {
            "name": "synthesize_memories(memory_uuids, focus?)",
            "emoji": "🔗",
            "priority": "COMBINE IDEAS",
            "purpose": "Combine related memories into unified insights",
            "example": 'synthesize_memories("uuid1,uuid2,uuid3", "patterns")',
            "returns": "Synthesized breakthrough combining input memories",
            "when_to_use": "Finding connections between separate ideas or memories"
        }
    ],
    "config": {
        "required": {
            "EPIPHANY_POLISHER_DATABASE_PATH": "/path/to/database.db",
            "EPIPHANY_POLISHER_ACTOR_UUID": "your-actor-uuid"
        },
        "optional": {
            "EPIPHANY_POLISHER_MODEL": "epiphany-polisher-qwen25:7b"
        },
        "prerequisites": [
            "✅ **Ollama running locally** with epiphany-polisher model",
            "✅ **Memory database access** for synthesis",
            "⭐ **Creative thinking tasks** benefit most from this server"
        ]
    }
}

def main():
    """Generate README functions for common MCP servers"""
    
    print("📖 MCP README Template Generator")
    print("=" * 50)
    
    # Generate Memory Maker README
    memory_maker_readme = create_readme_function(**MEMORY_MAKER_CONFIG)
    print("Memory Maker README function generated")
    
    # Generate Epiphany Polisher README  
    epiphany_readme = create_readme_function(**EPIPHANY_POLISHER_CONFIG)
    print("Epiphany Polisher README function generated")
    
    print("\n✅ README template system ready!")
    print("💡 Add these functions as the FIRST @mcp.tool() in each server")


if __name__ == "__main__":
    main()