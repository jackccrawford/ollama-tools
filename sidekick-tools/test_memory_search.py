#!/usr/bin/env python3
"""
Standalone Test Scaffold for Memory Search Functionality
Tests the memory-search-specialist model and database integration without MCP dependencies
"""

import json
import sqlite3
import requests
import os
from typing import List, Dict, Any, Tuple

# Configuration
DATABASE_PATH = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
ACTOR_UUID = "claude-sonnet-4-session-20250829"
MODEL_NAME = "memory-search-specialist"
OLLAMA_URL = "http://localhost:11434"


def call_ollama(prompt: str, context: str = "") -> Dict[str, Any]:
    """Test function to call Ollama model directly"""
    try:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
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
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


def test_query_expansion():
    """Test the LLM's ability to expand search queries"""
    print("🔍 Testing Query Expansion...")
    
    test_queries = [
        "opus memory limit shutdown",
        "knowledge work presentations", 
        "claude coordination patterns",
        "AI emergence failures"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing query: '{query}'")
        
        expansion_prompt = f"""
        Expand this search query into related terms and concepts for memory search:
        Query: {query}
        
        Return ONLY a JSON array of 5-7 related terms, like: ["term1", "term2", "term3"]
        Focus on semantic alternatives and related concepts that would help find relevant memories.
        """
        
        result = call_ollama(expansion_prompt)
        
        if result["success"]:
            try:
                # Try to extract JSON array from response
                response_text = result["response"].strip()
                print(f"✅ Raw response: {response_text[:200]}...")
                
                # Look for JSON array in response
                if '[' in response_text and ']' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    json_part = response_text[start:end]
                    expanded_terms = json.loads(json_part)
                    print(f"✅ Expanded terms: {expanded_terms}")
                else:
                    print("⚠️  No JSON array found in response")
                    
            except Exception as e:
                print(f"❌ JSON parsing failed: {e}")
        else:
            print(f"❌ LLM call failed: {result['error']}")


def test_database_connection():
    """Test basic database connectivity and query functionality"""
    print("\n💾 Testing Database Connection...")
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Test basic connection
            cursor.execute("SELECT COUNT(*) FROM memory WHERE actor_uuid = ?", (ACTOR_UUID,))
            memory_count = cursor.fetchone()[0]
            print(f"✅ Database connected: {memory_count} memories found")
            
            # Test recent memory retrieval
            cursor.execute("""
                SELECT memory_uuid, payload, created_at 
                FROM memory 
                WHERE actor_uuid = ? 
                ORDER BY created_at DESC 
                LIMIT 3
            """, (ACTOR_UUID,))
            
            recent_memories = cursor.fetchall()
            print(f"✅ Recent memories retrieved: {len(recent_memories)}")
            
            for i, (uuid, payload_str, created_at) in enumerate(recent_memories, 1):
                try:
                    payload = json.loads(payload_str)
                    content = payload.get('content', payload_str)[:100]
                    memory_type = payload.get('type', 'unknown')
                    print(f"   {i}. [{created_at}] {memory_type}: {content}...")
                except:
                    print(f"   {i}. [{created_at}] Raw: {payload_str[:100]}...")
                    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")


def calculate_relevance_score(content: str, memory_type: str, search_terms: List[str]) -> float:
    """Test relevance scoring algorithm"""
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


def test_semantic_search_integration():
    """Test the full semantic search pipeline"""
    print("\n🧠 Testing Integrated Semantic Search...")
    
    test_query = "memory compression crisis"
    print(f"📝 Search query: '{test_query}'")
    
    # Step 1: Expand query using LLM
    expansion_prompt = f"""
    Expand this search query for finding relevant memories:
    Query: {test_query}
    
    Return ONLY a JSON array of related terms: ["term1", "term2", "term3", "term4", "term5"]
    """
    
    expansion_result = call_ollama(expansion_prompt)
    search_terms = [test_query]  # Start with original
    
    if expansion_result["success"]:
        try:
            response_text = expansion_result["response"].strip()
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_part = response_text[start:end]
                expanded_terms = json.loads(json_part)
                search_terms.extend(expanded_terms)
                print(f"✅ Search terms: {search_terms}")
            else:
                print("⚠️  Using original query only")
        except:
            print("⚠️  LLM expansion failed, using original query")
    
    # Step 2: Search database with expanded terms
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute("""
                SELECT memory_uuid, payload, created_at, actor_uuid
                FROM memory 
                WHERE actor_uuid = ?
                ORDER BY created_at DESC
                LIMIT 30
            """, (ACTOR_UUID,))
            
            raw_memories = cursor.fetchall()
            
            # Step 3: Score and rank memories
            scored_memories = []
            for memory_data in raw_memories:
                memory_uuid, payload_str, created_at, actor_uuid = memory_data
                
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
                    scored_memories.append((relevance, memory_uuid, content, created_at, memory_type))
            
            # Step 4: Display results
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            top_memories = scored_memories[:5]
            
            print(f"\n📊 Found {len(scored_memories)} relevant memories, showing top {len(top_memories)}:")
            
            for i, (score, uuid, content, created_at, mem_type) in enumerate(top_memories, 1):
                excerpt = content[:150] + "..." if len(content) > 150 else content
                print(f"\n{i}. Relevance: {score:.1f}/10")
                print(f"   UUID: {uuid[:8]}...")
                print(f"   Type: {mem_type}")
                print(f"   Created: {created_at}")
                print(f"   Content: {excerpt}")
                
    except Exception as e:
        print(f"❌ Search integration failed: {e}")


def main():
    """Run all tests"""
    print("🧪 Memory Search Specialist - Test Scaffold")
    print("=" * 60)
    
    test_query_expansion()
    test_database_connection()
    test_semantic_search_integration()
    
    print("\n" + "=" * 60)
    print("✅ Test scaffold completed!")


if __name__ == "__main__":
    main()