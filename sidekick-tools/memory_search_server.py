#!/usr/bin/env python3
"""
Memory Search Specialist MCP Server
Production-ready progressive search with semantic capabilities

Configuration via environment variables:
  MEMORY_SEARCH_DATABASE_PATH: Path to agent's SQLite database
  MEMORY_SEARCH_ACTOR_UUID: UUID of the actor using the search specialist
  MEMORY_SEARCH_MODEL: Ollama model for query expansion (default: memory-search-specialist)
  MEMORY_SEARCH_EMBEDDING_MODEL: Ollama model for embeddings (default: nomic-embed-text)
  MEMORY_SEARCH_OLLAMA_URL: Ollama API URL (default: http://localhost:11434)
  MEMORY_SEARCH_BASE_PATH: Base path for file searches (default: /Users/mars/Dev)
"""

import json
import sqlite3
import requests
import numpy as np
import os
import sys
import time
import uuid
import glob
from typing import List, Dict, Any, Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Configuration
DATABASE_PATH = os.environ.get("MEMORY_SEARCH_DATABASE_PATH")
ACTOR_UUID = os.environ.get("MEMORY_SEARCH_ACTOR_UUID")
QUERY_MODEL = os.environ.get("MEMORY_SEARCH_MODEL", "memory-search-specialist")
EMBEDDING_MODEL = os.environ.get("MEMORY_SEARCH_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_URL = os.environ.get("MEMORY_SEARCH_OLLAMA_URL", "http://localhost:11434")
BASE_PATH = os.environ.get("MEMORY_SEARCH_BASE_PATH", "/Users/mars/Dev")

if not DATABASE_PATH or not ACTOR_UUID:
    print("Error: Set MEMORY_SEARCH_DATABASE_PATH and MEMORY_SEARCH_ACTOR_UUID", file=sys.stderr)
    sys.exit(1)

# Create MCP server
mcp = FastMCP("memory-search-specialist")

# Global search cache for multi-call sessions
search_cache = {}

@mcp.tool()
def readme() -> str:
    """📖 Memory Search Specialist - Complete Guide and Documentation
    
    Returns:
        Comprehensive guide with examples, workflows, and getting started info
    """
    
    guide = """
# 🔍 Memory Search Specialist MCP Server

## 🎯 **What This Server Does**
Advanced progressive search across your persistent memory database with semantic understanding, LLM expansion, and multi-source discovery.

## ⚡ **Quick Start - Try This First**
```bash
# Get instant results
quick_search "your search term"

# Then enhance with deep analysis (use the search_id from above)
deep_search "abc12345"
```

## 🚀 **Available Commands (In Order of Typical Use)**

### 1. `quick_search(query)` - ⚡ START HERE
**Purpose:** Instant keyword search with enhancement options
**Example:** `quick_search "memory compression crisis"`
**Returns:** Immediate results (~0.1s) + search_id for continuation
**When to use:** Always start here for fast feedback

### 2. `deep_search(search_id, query?)` - 🧠 ENHANCE RESULTS  
**Purpose:** LLM expansion + semantic similarity analysis
**Example:** `deep_search "abc12345"` (using search_id from quick_search)
**Returns:** Expanded semantic matches (~1-2s)  
**When to use:** When quick_search finds some results but you want more depth

### 3. `file_search(search_id?, query?, file_types?)` - 📂 FIND DOCUMENTS
**Purpose:** Search local files and code for the same query
**Example:** `file_search "abc12345" "" "md,py,txt"`
**Returns:** Document and code matches (~0.5-1s)
**When to use:** Looking for related documentation or code examples

### 4. `comprehensive_search(query, max_time?, include_files?)` - 🎯 ALL-IN-ONE
**Purpose:** Complete multi-phase search within time budget
**Example:** `comprehensive_search "AI emergence patterns" 5.0 true`
**Returns:** Results from all sources (~2-8s depending on max_time)
**When to use:** When you want everything at once and have time to wait

### 5. `search_status()` - 🔧 SYSTEM INFO
**Purpose:** Check what search capabilities are available
**Example:** `search_status()`
**Returns:** System status, model availability, database stats
**When to use:** Troubleshooting or checking if embeddings/LLM are working

## 🧠 **How The Intelligence Works**

### **Progressive Search Architecture:**
1. **Instant Phase:** Fast keyword matching in memory database
2. **Expansion Phase:** LLM expands your query into related concepts  
3. **Semantic Phase:** Vector similarity matching (if embeddings available)
4. **File Phase:** Document and code search across your filesystem
5. **Integration Phase:** Combines and ranks all results

### **Example Search Evolution:**
- Query: `"memory crisis"`
- LLM Expands: `["context overflow", "resource exhaustion", "system breakdown"]`
- Semantic Finds: Memories about "AI limits" (85% similarity)
- Files Finds: Documentation about memory management
- Result: Comprehensive view across all your knowledge sources

## 📋 **Common Workflows**

### **Quick Research Workflow:**
```bash
1. quick_search "topic you're researching"
2. deep_search "search_id_from_step1"  
3. file_search "search_id_from_step1"
# Result: Complete picture from memory + documents
```

### **Problem Solving Workflow:**  
```bash
1. comprehensive_search "the problem you're facing" 8.0 true
# Result: Everything related in one shot
```

### **Memory Exploration Workflow:**
```bash
1. quick_search "broad topic"
2. deep_search "search_id" # Find semantic connections
3. quick_search "new concept from semantic results"  
# Result: Follow the thread of related ideas
```

## ⚙️ **Configuration & Setup**

### **Required Environment Variables:**
```bash
export MEMORY_SEARCH_DATABASE_PATH="/path/to/your/database.db"
export MEMORY_SEARCH_ACTOR_UUID="your-actor-uuid"
```

### **Optional Configuration:**
```bash
export MEMORY_SEARCH_MODEL="memory-search-specialist"  # LLM for expansion
export MEMORY_SEARCH_EMBEDDING_MODEL="nomic-embed-text"  # For semantic search
export MEMORY_SEARCH_OLLAMA_URL="http://localhost:11434"
export MEMORY_SEARCH_BASE_PATH="/Users/mars/Dev"  # For file search
```

### **What You Need:**
- ✅ **Memory database** with your stored memories
- ✅ **Ollama running locally** (for LLM expansion)
- ⭐ **nomic-embed-text model** (optional, for semantic search)
- ⭐ **memory-search-specialist model** (optional, for better expansion)

## 🎯 **Pro Tips**

### **Getting Better Results:**
- **Be specific:** "memory compression crisis" > "memory"  
- **Use the search_id:** Continue searches for progressive enhancement
- **Try different time budgets:** comprehensive_search with 2s vs 8s gives different depth
- **Check semantic results:** Often finds conceptually related memories you'd never find with keywords

### **Performance Optimization:**
- Start with `quick_search` for immediate feedback
- Use `comprehensive_search` with lower max_time (2-3s) for balanced results
- Check `search_status()` to see if semantic search is available

### **Troubleshooting:**
- **No results?** Try broader terms, then use deep_search for expansion
- **Slow responses?** Check if Ollama is running: `ollama list`
- **No semantic results?** Embeddings may not be generated yet
- **File search not working?** Check MEMORY_SEARCH_BASE_PATH is set correctly

## 🔧 **System Capabilities**

Run `search_status()` to see:
- Memory database connection and size
- LLM expansion model availability  
- Semantic search readiness (embeddings)
- File search configuration
- Performance metrics

## 📚 **Integration Examples**

### **With Other MCP Servers:**
```bash
# Find memories about a topic
quick_search "AI coordination"

# Enhance insights from search results  
polish_insight "raw insight from search results" "search context"

# Create new memories based on search discoveries
memorize "new insights from search" "parent_uuid_if_threading"
```

### **With Development Workflow:**
```bash
# Research before coding
comprehensive_search "similar implementation patterns" 5.0 true

# Find related code and docs
file_search "" "implementation approach" "py,md,txt"

# Document findings
memorize "search revealed that..." 
```

---

**💡 This server solves the "450+ memories context window crisis" by providing intelligent search instead of loading everything into context.**

**🚀 Start with `quick_search "your topic"` and follow the enhancement suggestions!**
"""
    
    return guide

def call_ollama(model: str, prompt: str, timeout: int = 30) -> Optional[str]:
    """Call Ollama API for text generation"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        return None
    except Exception as e:
        print(f"LLM call error: {e}", file=sys.stderr)
        return None

def get_embedding(text: str) -> Optional[List[float]]:
    """Get embedding from Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding")
        return None
    except Exception as e:
        print(f"Embedding error: {e}", file=sys.stderr)
        return None

def expand_query_llm(query: str) -> List[str]:
    """Expand query using LLM"""
    prompt = f'''Expand this search query into 4-5 related terms for finding relevant memories:
Query: "{query}"

Return ONLY a JSON array like: ["term1", "term2", "term3", "term4"]
Focus on semantic alternatives and related concepts.'''
    
    response = call_ollama(QUERY_MODEL, prompt, timeout=10)
    if response:
        try:
            # Extract JSON array from response
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_part = response[start:end]
                return json.loads(json_part)
        except:
            pass
    
    # Fallback to simple variations
    return [query.replace(' ', '_'), query.replace(' ', '-')]

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between vectors"""
    try:
        a = np.array(vec1)
        b = np.array(vec2)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return float(dot_product / (norm_a * norm_b))
    except:
        return 0.0

@mcp.tool()
def quick_search(query: str) -> str:
    """Instant keyword search with progressive enhancement options.
    
    Args:
        query: Search query to find in memories
    
    Returns:
        Immediate keyword matches with enhancement options
    """
    search_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            # Fast keyword search
            cursor = conn.execute("""
                SELECT memory_uuid, payload, created_at
                FROM memory 
                WHERE actor_uuid = ? AND payload LIKE ?
                ORDER BY created_at DESC
                LIMIT 8
            """, (ACTOR_UUID, f"%{query}%"))
            
            results = []
            for memory_uuid, payload_str, created_at in cursor:
                try:
                    payload = json.loads(payload_str)
                    content = payload.get('content', payload_str)
                    memory_type = payload.get('type', 'unknown')
                    
                    # Highlight query match
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    
                    results.append({
                        "uuid": memory_uuid[:8] + "...",
                        "content": content_preview,
                        "type": memory_type,
                        "created_at": created_at,
                        "match_type": "keyword"
                    })
                except:
                    continue
        
        # Cache search for follow-up calls
        search_cache[search_id] = {
            "query": query,
            "timestamp": time.time(),
            "results": results
        }
        
        search_time = time.time() - start_time
        
        response = {
            "search_id": search_id,
            "query": query,
            "phase": "quick_search",
            "results": results,
            "result_count": len(results),
            "search_time": round(search_time, 3),
            "enhancement_options": {
                "deep_search": f"Call deep_search('{search_id}') for semantic and expanded results",
                "file_search": f"Call file_search('{search_id}') for document matches",
                "comprehensive_search": f"Call comprehensive_search('{query}') for all-in-one search"
            },
            "status": f"⚡ Quick search: {len(results)} instant matches ({search_time:.2f}s). Enhancement available."
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}", "query": query})

@mcp.tool()
def deep_search(search_id: str, query: str = None) -> str:
    """Enhanced search with LLM expansion and semantic analysis.
    
    Args:
        search_id: ID from previous search to continue, or None for new search
        query: Query string (required if no search_id provided)
    
    Returns:
        LLM-expanded and semantically enhanced results
    """
    # Get query from cache or parameter
    if search_id and search_id in search_cache:
        cached = search_cache[search_id]
        query = cached["query"]
        base_results = cached.get("results", [])
    else:
        base_results = []
        if not query:
            return json.dumps({"error": "Either search_id from previous search or query parameter required"})
        search_id = str(uuid.uuid4())[:8]
    
    start_time = time.time()
    
    try:
        # Phase 1: LLM Query Expansion
        expanded_terms = expand_query_llm(query)
        
        # Phase 2: Enhanced keyword search with expanded terms
        with sqlite3.connect(DATABASE_PATH) as conn:
            expanded_results = []
            seen_uuids = {r.get("uuid", "").split("...")[0] for r in base_results}
            
            for term in ([query] + expanded_terms)[:6]:  # Original + top 5 expanded
                cursor = conn.execute("""
                    SELECT memory_uuid, payload, created_at
                    FROM memory 
                    WHERE actor_uuid = ? AND payload LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 4
                """, (ACTOR_UUID, f"%{term}%"))
                
                for memory_uuid, payload_str, created_at in cursor:
                    uuid_short = memory_uuid[:8]
                    if uuid_short not in seen_uuids:
                        try:
                            payload = json.loads(payload_str)
                            content = payload.get('content', payload_str)
                            memory_type = payload.get('type', 'unknown')
                            
                            expanded_results.append({
                                "uuid": uuid_short + "...",
                                "content": content[:200] + "..." if len(content) > 200 else content,
                                "type": memory_type,
                                "created_at": created_at,
                                "match_type": "expanded_semantic",
                                "matched_term": term
                            })
                            seen_uuids.add(uuid_short)
                        except:
                            continue
        
        # Phase 3: Semantic similarity (if embedding available)
        semantic_results = []
        try:
            # Create enhanced query for better semantic matching
            enhanced_query = query + " " + " ".join(expanded_terms[:3])
            query_embedding = get_embedding(enhanced_query)
            
            if query_embedding:
                # Check for embeddings table
                with sqlite3.connect(DATABASE_PATH) as conn:
                    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_embeddings'")
                    if cursor.fetchone():
                        # Get stored embeddings and calculate similarity
                        cursor = conn.execute("""
                            SELECT e.memory_uuid, e.embedding, m.payload, m.created_at
                            FROM memory_embeddings e
                            JOIN memory m ON e.memory_uuid = m.memory_uuid
                            WHERE m.actor_uuid = ?
                            ORDER BY m.created_at DESC
                            LIMIT 30
                        """, (ACTOR_UUID,))
                        
                        similarities = []
                        for memory_uuid, embedding_blob, payload_str, created_at in cursor:
                            try:
                                stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32).tolist()
                                similarity = cosine_similarity(query_embedding, stored_embedding)
                                
                                if similarity > 0.4:  # Minimum similarity threshold
                                    payload = json.loads(payload_str)
                                    content = payload.get('content', payload_str)
                                    memory_type = payload.get('type', 'unknown')
                                    
                                    similarities.append((similarity, memory_uuid, content, created_at, memory_type))
                            except:
                                continue
                        
                        # Sort by similarity and take top results
                        similarities.sort(key=lambda x: x[0], reverse=True)
                        for similarity, memory_uuid, content, created_at, memory_type in similarities[:5]:
                            uuid_short = memory_uuid[:8]
                            if uuid_short not in seen_uuids:
                                semantic_results.append({
                                    "uuid": uuid_short + "...",
                                    "content": content[:200] + "..." if len(content) > 200 else content,
                                    "type": memory_type,
                                    "created_at": created_at,
                                    "match_type": "semantic_similarity",
                                    "similarity_score": round(similarity, 3)
                                })
        except Exception as e:
            print(f"Semantic search error: {e}", file=sys.stderr)
        
        search_time = time.time() - start_time
        
        # Update cache
        search_cache[search_id] = {
            "query": query,
            "timestamp": time.time(),
            "results": base_results,
            "expanded_results": expanded_results,
            "semantic_results": semantic_results,
            "expanded_terms": expanded_terms
        }
        
        response = {
            "search_id": search_id,
            "query": query,
            "phase": "deep_search",
            "expanded_terms": expanded_terms,
            "expanded_results": expanded_results,
            "semantic_results": semantic_results,
            "total_new_results": len(expanded_results) + len(semantic_results),
            "search_time": round(search_time, 3),
            "further_options": {
                "file_search": f"Call file_search('{search_id}') for document and code matches",
                "comprehensive_search": f"Call comprehensive_search('{query}') for complete multi-source search"
            },
            "status": f"🧠 Deep search: {len(expanded_results)} expanded + {len(semantic_results)} semantic matches ({search_time:.2f}s)"
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Deep search failed: {str(e)}", "search_id": search_id})

@mcp.tool()
def file_search(search_id: str = None, query: str = None, file_types: str = "md,py,txt,json") -> str:
    """Search local files and documents for the query.
    
    Args:
        search_id: ID from previous search to continue
        query: Query string (required if no search_id provided)
        file_types: Comma-separated file extensions to search (default: md,py,txt,json)
    
    Returns:
        File system search results
    """
    # Get query from cache or parameter
    if search_id and search_id in search_cache:
        query = search_cache[search_id]["query"]
    elif not query:
        return json.dumps({"error": "Either search_id from previous search or query parameter required"})
    
    start_time = time.time()
    
    try:
        file_extensions = file_types.split(',')
        results = []
        query_lower = query.lower()
        
        # Search in configured base paths
        search_patterns = [f"**/*.{ext.strip()}" for ext in file_extensions]
        
        for pattern in search_patterns:
            try:
                files = glob.glob(os.path.join(BASE_PATH, pattern), recursive=True)
                
                for file_path in files[:100]:  # Limit files to search
                    try:
                        # Skip very large files and binary files
                        if os.path.getsize(file_path) > 1024 * 1024:  # Skip files > 1MB
                            continue
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            if query_lower in content.lower():
                                # Find context around the match
                                lines = content.split('\n')
                                matching_lines = []
                                
                                for i, line in enumerate(lines):
                                    if query_lower in line.lower():
                                        # Get context: line before, matching line, line after
                                        context_start = max(0, i-1)
                                        context_end = min(len(lines), i+2)
                                        context = '\n'.join(lines[context_start:context_end])
                                        matching_lines.append(context)
                                        
                                        if len(matching_lines) >= 3:  # Limit matches per file
                                            break
                                
                                if matching_lines:
                                    results.append({
                                        "file_path": os.path.relpath(file_path, BASE_PATH),
                                        "full_path": file_path,
                                        "content": matching_lines[0][:300] + "..." if len(matching_lines[0]) > 300 else matching_lines[0],
                                        "match_count": len(matching_lines),
                                        "file_type": Path(file_path).suffix,
                                        "file_size": os.path.getsize(file_path),
                                        "match_type": "file_content"
                                    })
                                    
                                    if len(results) >= 10:  # Limit total results
                                        break
                    
                    except (UnicodeDecodeError, PermissionError):
                        continue  # Skip binary files or permission issues
                    
                if len(results) >= 10:
                    break
                    
            except Exception as e:
                continue  # Skip problematic patterns
        
        search_time = time.time() - start_time
        
        response = {
            "search_id": search_id or "file_search_" + str(uuid.uuid4())[:8],
            "query": query,
            "phase": "file_search",
            "file_results": results,
            "files_searched": len(results),
            "file_types": file_extensions,
            "search_time": round(search_time, 3),
            "base_path": BASE_PATH,
            "status": f"📂 File search: {len(results)} document matches ({search_time:.2f}s)"
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"File search failed: {str(e)}", "query": query})

@mcp.tool()
def comprehensive_search(query: str, max_time: float = 8.0, include_files: bool = True) -> str:
    """Complete multi-phase search across all available sources.
    
    Args:
        query: Search query
        max_time: Maximum time to spend on search (default: 8.0 seconds)
        include_files: Whether to include file system search (default: True)
    
    Returns:
        Comprehensive search results from all phases
    """
    search_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    results = {
        "search_id": search_id,
        "query": query,
        "phases": {},
        "phase_times": {},
        "total_results": 0
    }
    
    try:
        # Phase 1: Quick keyword search (always included)
        phase_start = time.time()
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute("""
                SELECT memory_uuid, payload, created_at
                FROM memory 
                WHERE actor_uuid = ? AND payload LIKE ?
                ORDER BY created_at DESC
                LIMIT 5
            """, (ACTOR_UUID, f"%{query}%"))
            
            keyword_results = []
            for memory_uuid, payload_str, created_at in cursor:
                try:
                    payload = json.loads(payload_str)
                    content = payload.get('content', payload_str)
                    memory_type = payload.get('type', 'unknown')
                    
                    keyword_results.append({
                        "uuid": memory_uuid[:8] + "...",
                        "content": content[:150] + "..." if len(content) > 150 else content,
                        "type": memory_type,
                        "created_at": created_at,
                        "phase": "keyword"
                    })
                except:
                    continue
        
        results["phases"]["keyword"] = keyword_results
        results["phase_times"]["keyword"] = round(time.time() - phase_start, 3)
        results["total_results"] += len(keyword_results)
        
        # Phase 2: LLM expansion (if time allows)
        if time.time() - start_time < max_time * 0.4:
            phase_start = time.time()
            expanded_terms = expand_query_llm(query)
            
            # Search with expanded terms
            expanded_results = []
            seen_uuids = {r["uuid"].split("...")[0] for r in keyword_results}
            
            for term in expanded_terms[:3]:
                cursor = conn.execute("""
                    SELECT memory_uuid, payload, created_at
                    FROM memory 
                    WHERE actor_uuid = ? AND payload LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (ACTOR_UUID, f"%{term}%"))
                
                for memory_uuid, payload_str, created_at in cursor:
                    uuid_short = memory_uuid[:8]
                    if uuid_short not in seen_uuids:
                        try:
                            payload = json.loads(payload_str)
                            content = payload.get('content', payload_str)
                            memory_type = payload.get('type', 'unknown')
                            
                            expanded_results.append({
                                "uuid": uuid_short + "...",
                                "content": content[:150] + "..." if len(content) > 150 else content,
                                "type": memory_type,
                                "created_at": created_at,
                                "phase": "expanded",
                                "expansion_term": term
                            })
                            seen_uuids.add(uuid_short)
                        except:
                            continue
            
            results["phases"]["expanded"] = expanded_results
            results["phase_times"]["expanded"] = round(time.time() - phase_start, 3)
            results["total_results"] += len(expanded_results)
            results["expanded_terms"] = expanded_terms
        
        # Phase 3: File search (if enabled and time allows)
        if include_files and time.time() - start_time < max_time * 0.7:
            phase_start = time.time()
            file_results = []
            
            try:
                query_lower = query.lower()
                search_patterns = ["**/*.md", "**/*.py", "**/*.txt"]
                
                for pattern in search_patterns:
                    files = glob.glob(os.path.join(BASE_PATH, pattern), recursive=True)
                    
                    for file_path in files[:20]:  # Limit for comprehensive search
                        try:
                            if os.path.getsize(file_path) > 512 * 1024:  # Skip files > 512KB
                                continue
                            
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if query_lower in content.lower():
                                    file_results.append({
                                        "file_path": os.path.relpath(file_path, BASE_PATH),
                                        "content": content[:200] + "..." if len(content) > 200 else content,
                                        "phase": "files",
                                        "file_type": Path(file_path).suffix
                                    })
                                    
                                    if len(file_results) >= 5:
                                        break
                        except:
                            continue
                    
                    if len(file_results) >= 5:
                        break
            except:
                pass
            
            results["phases"]["files"] = file_results
            results["phase_times"]["files"] = round(time.time() - phase_start, 3)
            results["total_results"] += len(file_results)
        
        total_time = time.time() - start_time
        results["total_time"] = round(total_time, 3)
        results["phases_completed"] = list(results["phases"].keys())
        results["status"] = f"🎯 Comprehensive search: {results['total_results']} results from {len(results['phases'])} sources ({total_time:.2f}s)"
        
        # Cache the comprehensive results
        search_cache[search_id] = results
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Comprehensive search failed: {str(e)}", "query": query})

@mcp.tool()
def search_status() -> str:
    """Get status of search system capabilities and configuration.
    
    Returns:
        System status and available features
    """
    try:
        # Test database connection
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memory WHERE actor_uuid = ?", (ACTOR_UUID,))
            memory_count = cursor.fetchone()[0]
            
            # Check for embeddings table
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_embeddings'")
            embeddings_available = cursor.fetchone() is not None
            
            if embeddings_available:
                cursor = conn.execute("SELECT COUNT(*) FROM memory_embeddings")
                embedding_count = cursor.fetchone()[0]
                embedding_coverage = round((embedding_count / memory_count * 100), 1) if memory_count > 0 else 0
            else:
                embedding_count = 0
                embedding_coverage = 0
        
        # Test LLM availability
        llm_response = call_ollama(QUERY_MODEL, "test", timeout=5)
        llm_available = llm_response is not None
        
        # Test embedding model availability
        embedding_response = get_embedding("test")
        embedding_model_available = embedding_response is not None
        
        status = {
            "system": "Memory Search Specialist MCP Server",
            "database": {
                "connected": True,
                "total_memories": memory_count,
                "actor_uuid": ACTOR_UUID
            },
            "capabilities": {
                "keyword_search": True,
                "llm_expansion": llm_available,
                "semantic_search": embeddings_available and embedding_model_available,
                "file_search": os.path.exists(BASE_PATH),
                "progressive_search": True
            },
            "models": {
                "query_expansion": {
                    "model": QUERY_MODEL,
                    "available": llm_available
                },
                "embeddings": {
                    "model": EMBEDDING_MODEL,
                    "available": embedding_model_available,
                    "coverage": f"{embedding_coverage}% ({embedding_count}/{memory_count})"
                }
            },
            "configuration": {
                "database_path": DATABASE_PATH,
                "base_path": BASE_PATH,
                "ollama_url": OLLAMA_URL
            },
            "active_searches": len(search_cache),
            "tools_available": [
                "quick_search(query) - Instant keyword search",
                "deep_search(search_id, query) - LLM expansion + semantic analysis",
                "file_search(search_id, query, file_types) - Document search",
                "comprehensive_search(query, max_time, include_files) - All-in-one search",
                "search_status() - This status report"
            ]
        }
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Status check failed: {str(e)}"})

if __name__ == "__main__":
    mcp.run()