#!/usr/bin/env python3
"""
Epiphany Polisher README - Comprehensive documentation
"""

def generate_epiphany_polisher_readme() -> str:
    """Generate comprehensive Epiphany Polisher MCP server documentation"""
    
    readme = """
# ✨ Epiphany Polisher MCP Server

## 🎯 **What This Server Does**
Transform raw thoughts and observations into polished insights using cognitive enhancement AI. Think of it as your personal insight development lab that helps you articulate breakthrough understanding.

## ⚡ **Quick Start - Try This First**
```bash
# Always start with the guide
readme

# Polish a rough idea into a clear insight
polish_insight "I think semantic search works better with query expansion" "search optimization research"
```

## 🚀 **Available Commands (In Order of Typical Use)**

### 1. `polish_insight(raw_insight, context?)` - ✨ START HERE
**Purpose:** Transform rough ideas into articulated insights with depth and clarity
**Example:** `polish_insight("AI agents seem to work better together", "distributed intelligence research")`
**Returns:** Enhanced insight with improved clarity, depth, and connections
**When to use:** When you have a vague idea that needs to be developed into a clear breakthrough

### 2. `generate_questions(topic_or_insight, question_type?)` - ❓ PROBE DEEPER
**Purpose:** Generate probing questions that reveal hidden patterns and assumptions
**Example:** `generate_questions("memory compression for AI", "probing")`
**Returns:** 5-7 thought-provoking questions with explanations
**When to use:** When you want to explore an insight more deeply or challenge assumptions

### 3. `connect_concepts(concept_a, concept_b, connection_type?)` - 🌐 FIND RELATIONSHIPS
**Purpose:** Discover unexpected relationships between disparate concepts
**Example:** `connect_concepts("memory compression", "progressive disclosure", "analogical")`
**Returns:** Analysis of connections between concepts with practical applications
**When to use:** When you suspect two ideas might be related but can't articulate how

### 4. `synthesize_memories(memory_uuids, synthesis_focus?)` - 🔗 COMBINE IDEAS
**Purpose:** Combine related memories into unified breakthrough insights
**Example:** `synthesize_memories("uuid1,uuid2,uuid3", "patterns")`
**Returns:** Synthesized insight combining the selected memories
**When to use:** When you have multiple related thoughts/memories that might form a bigger insight

### 5. `enhance_memory_payload(memory_uuid, enhancement_type?)` - 📈 UPGRADE EXISTING
**Purpose:** Enhance an existing memory with deeper insights and connections
**Example:** `enhance_memory_payload("abc123def", "comprehensive")`
**Returns:** Enhanced version of the memory with added depth and connections
**When to use:** When you want to revisit and deepen a previous insight or memory

## 🧠 **How The Enhancement Process Works**

### **Insight Development Pipeline:**
1. **Extract:** Identify the core insight or pattern from raw input
2. **Enhance:** Add depth, nuance, and clarity to the core idea
3. **Contextualize:** Place within broader frameworks and knowledge
4. **Question:** Generate inquiries that probe assumptions and reveal patterns
5. **Connect:** Link to related concepts and reveal implications

### **Example Enhancement Process:**
- **Raw Input:** "LLM query expansion seems to help search"
- **Polished Output:** Comprehensive analysis explaining why query expansion increases semantic embedding effectiveness by 17-44%, the cognitive science behind it, and applications to other domains
- **Generated Questions:** "What other areas could benefit from this expansion principle?"
- **Connected Concepts:** Links to progressive disclosure, cognitive load theory, information retrieval

## 📋 **Common Workflows**

### **Research & Development Workflow:**
```bash
1. polish_insight "your rough observation" "research context"
2. generate_questions "polished insight from step 1" "exploring"
3. connect_concepts "main concept" "related concept" "structural"
# Result: Deep understanding with new research directions
```

### **Memory Enhancement Workflow:**
```bash
1. enhance_memory_payload "memory-uuid" "comprehensive"
2. generate_questions "enhanced content" "probing" 
3. memorize "new insights from questions" "original-memory-uuid"
# Result: Upgraded memory with deeper understanding
```

### **Breakthrough Discovery Workflow:**
```bash
1. synthesize_memories "uuid1,uuid2,uuid3" "connections"
2. polish_insight "synthesis result" "breakthrough context"
3. connect_concepts "breakthrough" "existing knowledge" "emergent"
# Result: New breakthrough insight with clear articulation
```

## ⚙️ **Configuration & Setup**

### **Required Environment Variables:**
```bash
export EPIPHANY_POLISHER_DATABASE_PATH="/path/to/your/database.db"
export EPIPHANY_POLISHER_ACTOR_UUID="your-actor-uuid"
```

### **Optional Configuration:**
```bash
export EPIPHANY_POLISHER_MODEL="epiphany-polisher-qwen25:7b"  # Custom model
export EPIPHANY_POLISHER_OLLAMA_URL="http://localhost:11434"
```

### **What You Need:**
- ✅ **Ollama running locally** with epiphany-polisher model
- ✅ **Memory database access** for synthesis and enhancement
- ✅ **Creative thinking tasks** - this server excels at insight development
- ⭐ **Custom epiphany-polisher model** (optional, but recommended)

### **Model Setup:**
```bash
# Create the specialized epiphany polisher model
ollama create epiphany-polisher-qwen25:7b -f /path/to/epiphany-polisher.modelfile

# Or use a general model (less specialized but still functional)
# The server will work with qwen2.5:7b or similar models
```

## 🎯 **Pro Tips & Best Practices**

### **Getting Better Results:**
- **Provide context:** Always include the context parameter for better enhancement
- **Start with polish_insight:** It's the most fundamental and useful command
- **Be specific with raw insights:** "Memory search is hard" < "Memory search fails when context windows overflow"
- **Use question types:** "probing", "connecting", "challenging", "exploring" for different perspectives

### **Enhancement Types:**
- **comprehensive:** Complete analysis with all aspects (default)
- **connections:** Focus on linking to other concepts and domains
- **implications:** Explore deeper consequences and applications
- **questions:** Generate follow-up questions and research directions

### **Connection Types:**
- **analogical:** Find metaphorical and structural similarities
- **structural:** Analyze organizational and systemic patterns
- **functional:** Explore behavioral and operational parallels
- **emergent:** Identify new properties from combining concepts

### **Synthesis Focus Areas:**
- **patterns:** Look for recurring themes and structures
- **connections:** Find relationships between separate ideas
- **implications:** Explore consequences and applications
- **breakthrough:** Identify paradigm shifts and innovations

## 🔬 **Advanced Usage**

### **Multi-Step Enhancement:**
```bash
# Step 1: Polish rough insight
polish_insight "rough idea" "context"

# Step 2: Generate questions about polished insight
generate_questions "polished insight result" "challenging"

# Step 3: Connect to unexpected domains
connect_concepts "main insight" "surprising domain" "analogical"

# Step 4: Synthesize all discoveries
# (Save each step as memory, then synthesize the memory UUIDs)
```

### **Memory Network Enhancement:**
```bash
# Find related memories first (using memory search)
quick_search "topic area"

# Enhance the most promising memory
enhance_memory_payload "best-memory-uuid" "comprehensive"

# Generate questions about enhanced memory
generate_questions "enhanced content" "probing"

# Connect insights to broader knowledge
connect_concepts "insight theme" "broader domain" "structural"
```

## 📚 **Integration with Other MCP Servers**

### **With Memory Maker:**
```bash
# 1. Find memories to enhance
remember "topic area"

# 2. Enhance key memories
enhance_memory_payload "memory-uuid" "comprehensive"

# 3. Save enhanced insights
memorize "enhanced insight result" "original-memory-uuid"
```

### **With Memory Search Specialist:**
```bash
# 1. Search for related content
comprehensive_search "research topic" 8.0 true

# 2. Polish insights from search results
polish_insight "insight from search" "research context"

# 3. Connect to other discoveries
connect_concepts "search insight" "polished insight" "emergent"
```

### **With Sidekick Network:**
```bash
# 1. Get raw insights from network
sidekick "show me recent breakthrough patterns"

# 2. Polish the most promising insights
polish_insight "network insight" "distributed intelligence context"

# 3. Share polished insights back to network
memorize "polished breakthrough" "network-context-uuid"
```

## 🔧 **Troubleshooting**

### **"Model not found" errors:**
```bash
# Check if Ollama is running
ollama list

# Verify the epiphany-polisher model exists
ollama list | grep epiphany

# Create the model if missing (or use a general model)
export EPIPHANY_POLISHER_MODEL="qwen2.5:7b"
```

### **Poor enhancement quality:**
- **Add more context:** Include background information about your insight
- **Use specific language:** Vague inputs produce vague outputs
- **Try different enhancement types:** "connections" vs "comprehensive" vs "implications"
- **Provide examples:** Include examples or analogies in your raw insights

### **Memory synthesis not working:**
- **Check memory UUIDs:** Ensure the UUIDs exist in the database
- **Use valid syntax:** Comma-separated UUIDs: "uuid1,uuid2,uuid3"
- **Limit memory count:** 3-5 memories work better than 10+
- **Provide synthesis focus:** "patterns", "connections", "implications" guide the analysis

## 🌟 **Use Cases & Examples**

### **Research Enhancement:**
- **Raw:** "Users struggle with search interfaces"
- **Polished:** "Search interface complexity creates cognitive load that reduces discovery effectiveness, suggesting progressive disclosure and contextual assistance could improve user outcomes"

### **Problem Solving:**
- **Raw:** "Memory systems hit limits"  
- **Polished:** "Memory system constraints reveal the fundamental tension between storage capacity and retrieval speed, pointing toward hierarchical compression and semantic indexing as architectural solutions"

### **Innovation Development:**
- **Raw:** "AI agents could work together better"
- **Polished:** "Distributed AI coordination requires shared context management and specialization protocols, enabling emergent intelligence through complementary capabilities rather than redundant processing"

---

**💡 This server transforms rough ideas into breakthrough insights through cognitive enhancement AI!**

**🚀 Start with `polish_insight "your rough idea" "context"` and follow the enhancement suggestions!**

**✨ The goal is not just better writing - it's enhanced thinking itself!**
"""
    
    return readme


# Generate MCP tool function
def create_epiphany_polisher_readme_function():
    """Create the readme() function for the Epiphany Polisher MCP server"""
    
    readme_content = generate_epiphany_polisher_readme()
    
    function_code = f'''@mcp.tool()
def readme() -> str:
    """📖 Epiphany Polisher - Complete Guide and Documentation
    
    Returns:
        Comprehensive guide with examples, workflows, and getting started info
    """
    
    guide = """{readme_content}"""
    
    return guide'''
    
    return function_code


if __name__ == "__main__":
    print("✨ Epiphany Polisher README Generator")
    print("=" * 50)
    
    readme = generate_epiphany_polisher_readme()
    print(readme)
    
    print("\n" + "=" * 50)
    print("✅ Epiphany Polisher README generated!")
    print("💡 Add this as the first @mcp.tool() in the epiphany-polisher server")