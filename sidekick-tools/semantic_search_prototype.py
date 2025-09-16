#!/usr/bin/env python3
"""
True Semantic Search Prototype with Hybrid Approach
Uses nomic-embed-text for embeddings + enhanced keyword search
"""

import json
import sqlite3
import requests
import numpy as np
from typing import List, Dict, Any, Tuple
import os

# Configuration
DATABASE_PATH = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
ACTOR_UUID = "claude-sonnet-4-session-20250829"
QUERY_EXPANSION_MODEL = "memory-search-specialist"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434"


def get_embedding(text: str) -> Dict[str, Any]:
    """Generate embedding using nomic-embed-text model"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "embedding": result.get("embedding", []),
                "model": EMBEDDING_MODEL
            }
        else:
            return {
                "success": False,
                "error": f"Embedding API error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Embedding error: {str(e)}"
        }


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
    except:
        return 0.0


def expand_query_llm(query: str) -> List[str]:
    """Use LLM to expand query terms"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": QUERY_EXPANSION_MODEL,
                "prompt": f'Expand search query "{query}" into related terms. Return JSON array: ["term1", "term2", "term3"]',
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_part = response_text[start:end]
                return json.loads(json_part)
        
        return [query]  # Fallback to original query
    except:
        return [query]


def keyword_score(content: str, memory_type: str, search_terms: List[str]) -> float:
    """Calculate keyword-based relevance score"""
    score = 0.0
    content_lower = content.lower()
    type_lower = memory_type.lower()
    
    for term in search_terms:
        term_lower = term.lower()
        if term_lower in content_lower:
            score += 2.0
        if term_lower in type_lower:
            score += 1.5
    
    # High-value type bonus
    high_value_types = [
        'coordination_directive', 'architectural_insight', 'foundational_principle',
        'emergence_analysis', 'agent_role_definition', 'workflow_design'
    ]
    if memory_type in high_value_types:
        score += 1.0
        
    return score


def test_embedding_generation():
    """Test the nomic embedding model"""
    print("🔍 Testing Embedding Generation...")
    
    test_texts = [
        "memory compression crisis analysis",
        "AI emergence failure patterns", 
        "distributed coordination protocols",
        "knowledge work presentation generation"
    ]
    
    for text in test_texts:
        print(f"\n📝 Testing: '{text}'")
        result = get_embedding(text)
        
        if result["success"]:
            embedding = result["embedding"]
            print(f"✅ Embedding generated: {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
            
            # Test similarity with itself (should be 1.0)
            similarity = cosine_similarity(embedding, embedding)
            print(f"   Self-similarity: {similarity:.3f} (should be ~1.0)")
        else:
            print(f"❌ Embedding failed: {result['error']}")


def test_semantic_similarity():
    """Test semantic similarity between related concepts"""
    print("\n🧠 Testing Semantic Similarity...")
    
    test_pairs = [
        ("memory crisis", "context overflow"),
        ("AI coordination", "distributed intelligence"),
        ("emergence failure", "system breakdown"),
        ("knowledge work", "business presentations")
    ]
    
    for text1, text2 in test_pairs:
        print(f"\n📊 Comparing: '{text1}' vs '{text2}'")
        
        # Get embeddings
        emb1_result = get_embedding(text1)
        emb2_result = get_embedding(text2)
        
        if emb1_result["success"] and emb2_result["success"]:
            similarity = cosine_similarity(
                emb1_result["embedding"], 
                emb2_result["embedding"]
            )
            print(f"✅ Semantic similarity: {similarity:.3f}")
            
            # Also test keyword overlap (for comparison)
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            keyword_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
            print(f"📝 Keyword overlap: {keyword_overlap:.3f}")
        else:
            print("❌ Failed to generate embeddings")


def test_hybrid_search_prototype():
    """Test hybrid semantic + keyword search approach"""
    print("\n🔄 Testing Hybrid Search Prototype...")
    
    query = "memory compression crisis"
    print(f"🔍 Query: '{query}'")
    
    # Step 1: Generate query embedding
    query_embedding_result = get_embedding(query)
    if not query_embedding_result["success"]:
        print(f"❌ Query embedding failed: {query_embedding_result['error']}")
        return
    
    query_embedding = query_embedding_result["embedding"]
    print(f"✅ Query embedding: {len(query_embedding)} dimensions")
    
    # Step 2: Expand query with LLM
    expanded_terms = expand_query_llm(query)
    print(f"✅ Expanded terms: {expanded_terms}")
    
    # Step 3: Get recent memories for testing
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute("""
                SELECT memory_uuid, payload, created_at
                FROM memory 
                WHERE actor_uuid = ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (ACTOR_UUID,))
            
            memories = cursor.fetchall()
            print(f"✅ Retrieved {len(memories)} recent memories for testing")
            
            # Step 4: Calculate hybrid scores
            results = []
            for memory_uuid, payload_str, created_at in memories:
                try:
                    payload = json.loads(payload_str)
                    content = payload.get('content', payload_str)
                    memory_type = payload.get('type', 'unknown')
                    
                    # Generate embedding for this memory content
                    content_embedding_result = get_embedding(content[:500])  # Limit content length
                    
                    if content_embedding_result["success"]:
                        content_embedding = content_embedding_result["embedding"]
                        
                        # Semantic similarity score (0-1)
                        semantic_score = cosine_similarity(query_embedding, content_embedding)
                        
                        # Keyword score (0-10+)
                        keyword_score_val = keyword_score(content, memory_type, expanded_terms)
                        
                        # Hybrid score: weighted combination
                        hybrid_score = (semantic_score * 5.0) + (keyword_score_val * 0.5)
                        
                        results.append((
                            hybrid_score, semantic_score, keyword_score_val,
                            memory_uuid, content[:200], created_at, memory_type
                        ))
                    
                except Exception as e:
                    print(f"⚠️  Skipping memory {memory_uuid[:8]}: {e}")
                    continue
            
            # Step 5: Display results
            results.sort(key=lambda x: x[0], reverse=True)  # Sort by hybrid score
            
            print(f"\n📊 Hybrid Search Results (Top {min(5, len(results))}):")
            for i, (hybrid, semantic, keyword, uuid, content, created_at, mem_type) in enumerate(results[:5], 1):
                print(f"\n{i}. UUID: {uuid[:8]}...")
                print(f"   Hybrid Score: {hybrid:.2f} (Semantic: {semantic:.3f}, Keyword: {keyword:.1f})")
                print(f"   Type: {mem_type}")
                print(f"   Created: {created_at}")
                print(f"   Content: {content}...")
                
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")


def main():
    """Run semantic search tests"""
    print("🧪 Semantic Search Prototype - Test Suite")
    print("=" * 60)
    
    test_embedding_generation()
    test_semantic_similarity()
    test_hybrid_search_prototype()
    
    print("\n" + "=" * 60)
    print("✅ Semantic search prototype testing completed!")


if __name__ == "__main__":
    main()