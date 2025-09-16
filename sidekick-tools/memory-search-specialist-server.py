#!/usr/bin/env python3
"""
Memory Search Specialist MCP Server

A semantic search agent that uses local LLM to enhance memory queries and retrieval.
Based on the epiphany-polisher architecture but optimized for memory search tasks.

Configuration via environment variables:
  MEMORY_SEARCH_DATABASE_PATH: Path to agent's SQLite database for memory integration
  MEMORY_SEARCH_ACTOR_UUID: UUID of the actor using the search specialist
  MEMORY_SEARCH_MODEL: Ollama model name (default: memory-search-specialist)
  MEMORY_SEARCH_OLLAMA_URL: Ollama API URL (default: http://localhost:11434)
"""

import json
import sqlite3
import uuid
import os
import sys
import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP

# Configuration
DATABASE_PATH = os.environ.get("MEMORY_SEARCH_DATABASE_PATH")
ACTOR_UUID = os.environ.get("MEMORY_SEARCH_ACTOR_UUID")
MODEL_NAME = os.environ.get("MEMORY_SEARCH_MODEL", "memory-search-specialist")
OLLAMA_URL = os.environ.get("MEMORY_SEARCH_OLLAMA_URL", "http://localhost:11434")

if not DATABASE_PATH or not ACTOR_UUID:
    print("Error: Set MEMORY_SEARCH_DATABASE_PATH and MEMORY_SEARCH_ACTOR_UUID", file=sys.stderr)
    sys.exit(1)

# Create MCP server
mcp = FastMCP("memory-search-specialist")


def call_ollama(prompt: str, context: str = "") -> Dict[str, Any]:
    """Call the local Ollama API with the memory-search-specialist model
    
    Args:
        prompt: The main prompt/content to process
        context: Optional context to provide additional information
    
    Returns:
        Dict containing success status, response, or error
    """
    try:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": MODEL_NAME
            }
        else:
            return {
                "success": False,
                "error": f"Ollama API error: {response.status_code} - {response.text}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to connect to Ollama: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def get_memories_raw(query_sql: str, params: List, limit: int = 50) -> List[Tuple]:
    """Execute raw SQL query against memory database
    
    Args:
        query_sql: SQL query to execute
        params: Parameters for the query
        limit: Maximum number of results
    
    Returns:
        List of memory tuples
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute(query_sql, params)
            return cursor.fetchmany(limit)
    except Exception as e:
        print(f"Database query error: {e}", file=sys.stderr)
        return []


def calculate_relevance_score(content: str, memory_type: str, search_terms: List[str]) -> float:
    """Calculate relevance score for a memory based on search terms"""
    score = 0.0
    content_lower = content.lower()
    type_lower = memory_type.lower()
    
    # Exact match bonus
    for term in search_terms:
        term_lower = term.lower()
        if term_lower in content_lower:
            score += 2.0
        if term_lower in type_lower:
            score += 1.5
    
    # Semantic similarity (simple keyword proximity)
    content_words = content_lower.split()
    for term in search_terms:
        for word in content_words:
            if term.lower() in word or word in term.lower():
                score += 0.3
    
    # Type-based relevance boost
    high_value_types = [
        'coordination_directive', 'architectural_insight', 'foundational_principle',
        'emergence_analysis', 'agent_role_definition', 'workflow_design'
    ]
    if memory_type in high_value_types:
        score += 1.0
        
    return score


@mcp.tool()
def expand_search_query(query: str) -> str:
    """Use LLM to expand a search query into semantic concepts and related terms.
    
    Args:
        query: Original search query from user
    
    Returns:
        Expanded search concepts and strategy
    """
    prompt = f"""EXPAND THIS MEMORY SEARCH QUERY:

User Query: "{query}"

Your task is to expand this query into a comprehensive search strategy that includes:

1. CORE CONCEPTS: Extract the main concepts and themes
2. SEMANTIC ALTERNATIVES: Generate synonyms and related terms  
3. RELATED DOMAINS: Identify connected areas of knowledge
4. CONTEXT CLUES: Recognize temporal, categorical, or situational hints
5. SEARCH PRIORITIES: Rank terms by likely relevance

Provide your response in this JSON format:
{{
  "original_query": "{query}",
  "core_concepts": ["concept1", "concept2", "..."],
  "semantic_alternatives": ["alt1", "alt2", "..."],
  "related_domains": ["domain1", "domain2", "..."], 
  "temporal_hints": ["recent", "historical", "specific_timeframe"],
  "priority_terms": ["high_priority1", "high_priority2", "..."],
  "search_strategy": "description of recommended approach"
}}

Focus on semantic meaning and user intent, not just keywords."""

    result = call_ollama(prompt)
    
    if result["success"]:
        return f"🔍 **Query Expansion**:\n{result['response']}\n\n*Expanded by {MODEL_NAME}*"
    else:
        return f"❌ **Expansion Error**: {result['error']}"


@mcp.tool()
def semantic_memory_search(query: str, limit: int = 10, actor_filter: str = "") -> str:
    """Perform intelligent semantic search across memories using LLM query expansion.
    
    Args:
        query: Natural language search query
        limit: Maximum number of results to return
        actor_filter: Optional actor UUID to filter results
    
    Returns:
        Formatted search results with relevance scoring
    """
    try:
        # First, expand the query using LLM
        expansion_result = call_ollama(f"""
        Expand this search query into a list of related terms and concepts:
        Query: {query}
        
        Return only a JSON array of search terms, like: ["term1", "term2", "term3"]
        Focus on semantic alternatives and related concepts.
        """)
        
        # Parse expanded terms
        search_terms = [query]  # Start with original query
        if expansion_result["success"]:
            try:
                # Try to extract JSON array from response
                response_text = expansion_result["response"].strip()
                if response_text.startswith('[') and response_text.endswith(']'):
                    expanded_terms = json.loads(response_text)
                    search_terms.extend(expanded_terms)
            except:
                # If JSON parsing fails, split response on common delimiters
                expanded_text = expansion_result["response"]
                import re
                potential_terms = re.findall(r'"([^"]*)"', expanded_text)
                search_terms.extend(potential_terms[:10])  # Limit to 10 additional terms
        
        # Build SQL query
        if actor_filter:
            base_query = """
                SELECT m.memory_uuid, m.payload, m.created_at, m.actor_uuid,
                       COALESCE(a.display_name, m.actor_uuid) as actor_name
                FROM memory m
                LEFT JOIN actor a ON m.actor_uuid = a.actor_uuid  
                WHERE m.actor_uuid = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """
            params = [actor_filter, limit * 3]  # Get more to filter by relevance
        else:
            base_query = """
                SELECT m.memory_uuid, m.payload, m.created_at, m.actor_uuid,
                       COALESCE(a.display_name, m.actor_uuid) as actor_name
                FROM memory m
                LEFT JOIN actor a ON m.actor_uuid = a.actor_uuid
                ORDER BY m.created_at DESC
                LIMIT ?
            """
            params = [limit * 3]  # Get more to filter by relevance
        
        raw_memories = get_memories_raw(base_query, params)
        
        # Score and rank memories
        scored_memories = []
        for memory_data in raw_memories:
            memory_uuid, payload_str, created_at, actor_uuid, actor_name = memory_data
            
            try:
                payload = json.loads(payload_str)
                content = payload.get('content', '')
                memory_type = payload.get('type', 'unknown')
            except:
                content = payload_str
                memory_type = 'unknown'
            
            # Calculate relevance score
            relevance = calculate_relevance_score(content, memory_type, search_terms)
            
            if relevance > 0:
                scored_memories.append((relevance, memory_uuid, content, created_at, memory_type, actor_name))
        
        # Sort by relevance and take top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = scored_memories[:limit]
        
        # Format results
        if not top_memories:
            return f"🔍 No relevant memories found for: '{query}'"
        
        result_text = f"🧠 **Semantic Search Results** for: '{query}'\n"
        result_text += f"Expanded terms: {', '.join(search_terms[:5])}\n"
        result_text += "=" * 60 + "\n\n"
        
        for i, (score, uuid, content, created_at, mem_type, actor_name) in enumerate(top_memories, 1):
            excerpt = content[:200] + "..." if len(content) > 200 else content
            result_text += f"📄 **Result {i}** (Relevance: {score:.1f}/10)\n"
            result_text += f"   UUID: {uuid[:8]}...\n" 
            result_text += f"   Type: {mem_type}\n"
            result_text += f"   Actor: {actor_name}\n"
            result_text += f"   Created: {created_at}\n"
            result_text += f"   Content: {excerpt}\n"
            result_text += "-" * 40 + "\n"
        
        return result_text
        
    except Exception as e:
        return f"❌ **Search Error**: {str(e)}"


@mcp.tool()
def analyze_search_patterns(query_history: str) -> str:
    """Analyze patterns in search queries to improve future searches.
    
    Args:
        query_history: Comma-separated list of recent search queries
    
    Returns:
        Analysis of search patterns and recommendations
    """
    queries = [q.strip() for q in query_history.split(',') if q.strip()]
    
    prompt = f"""ANALYZE THESE SEARCH PATTERNS:

Recent queries: {queries}

Analyze these search queries to identify:
1. Common themes and interests
2. Knowledge gaps or recurring needs  
3. Temporal patterns (what's being searched when)
4. Suggested improvements for future searches
5. Recommended memory organization strategies

Provide insights that would help optimize future memory searches and storage."""

    result = call_ollama(prompt)
    
    if result["success"]:
        return f"📈 **Search Pattern Analysis**:\n{result['response']}\n\n*Analyzed by {MODEL_NAME}*"
    else:
        return f"❌ **Analysis Error**: {result['error']}"


@mcp.tool()
def suggest_memory_connections(memory_uuid: str) -> str:
    """Find and suggest related memories that might be connected to a specific memory.
    
    Args:
        memory_uuid: UUID of the memory to find connections for
    
    Returns:
        Suggested connections and relationships with other memories
    """
    try:
        # Get the target memory
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute(
                "SELECT payload, created_at FROM memory WHERE memory_uuid = ?",
                (memory_uuid,)
            )
            result = cursor.fetchone()
            
            if not result:
                return f"❌ Memory not found: {memory_uuid}"
            
            payload_str, created_at = result
            
            try:
                payload = json.loads(payload_str)
                content = payload.get('content', payload_str)
                memory_type = payload.get('type', 'unknown')
            except:
                content = payload_str
                memory_type = 'unknown'
        
        # Use LLM to extract key concepts for connection analysis
        concept_prompt = f"""
        Extract 3-5 key concepts from this memory that could be used to find related memories:
        
        Memory content: {content}
        Memory type: {memory_type}
        
        Return only a JSON array of concepts: ["concept1", "concept2", "concept3"]
        """
        
        concept_result = call_ollama(concept_prompt)
        
        if concept_result["success"]:
            # Parse concepts and search for related memories
            try:
                concepts_text = concept_result["response"].strip()
                if concepts_text.startswith('[') and concepts_text.endswith(']'):
                    concepts = json.loads(concepts_text)
                else:
                    import re
                    concepts = re.findall(r'"([^"]*)"', concepts_text)
                
                if concepts:
                    # Search for related memories using the concepts
                    related_search = semantic_memory_search(
                        query=' '.join(concepts),
                        limit=5,
                        actor_filter=""
                    )
                    
                    return f"🔗 **Memory Connections** for {memory_uuid[:8]}...\n\n**Key Concepts**: {', '.join(concepts)}\n\n{related_search}"
                    
            except Exception as e:
                return f"❌ Concept extraction failed: {str(e)}"
        
        return f"❌ Could not extract concepts from memory {memory_uuid[:8]}..."
        
    except Exception as e:
        return f"❌ **Connection Error**: {str(e)}"


if __name__ == "__main__":
    mcp.run()