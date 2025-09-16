#!/usr/bin/env python3
"""
Test: Does semantic search work better with expanded query terms?
Compare raw query vs LLM-expanded query embedding performance
"""

import json
import requests
import numpy as np
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
QUERY_EXPANSION_MODEL = "memory-search-specialist"

def get_embedding(text: str) -> List[float]:
    """Get embedding from Ollama"""
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=30
    )
    if response.status_code == 200:
        return response.json().get("embedding", [])
    return []

def expand_query(query: str) -> List[str]:
    """Expand query using LLM"""
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": QUERY_EXPANSION_MODEL,
            "prompt": f'Expand search query "{query}" into 5-7 related terms. Return JSON array: ["term1", "term2", "term3"]',
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
            try:
                return json.loads(json_part)
            except:
                return []
    return []

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity"""
    a = np.array(vec1)
    b = np.array(vec2)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return float(dot_product / (norm_a * norm_b))

def test_query_embedding_approaches():
    """Test different approaches to query embedding"""
    print("🧪 Testing Query Embedding Approaches...")
    
    # Test cases
    test_queries = [
        "memory compression crisis",
        "AI emergence failure",
        "knowledge work presentations",
        "distributed coordination"
    ]
    
    # Target content to match against
    target_contents = [
        "context window overflow causing system breakdown",
        "AI agent resource constraints leading to shutdown", 
        "business presentation generation for executives",
        "multi-agent collaboration protocols and patterns"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # Approach 1: Raw query embedding
        raw_embedding = get_embedding(query)
        print(f"✅ Raw query embedding: {len(raw_embedding)} dims")
        
        # Approach 2: Expanded query terms
        expanded_terms = expand_query(query)
        print(f"✅ Expanded terms: {expanded_terms}")
        
        # Approach 3: Combined expanded text embedding
        expanded_text = " ".join([query] + expanded_terms)
        expanded_embedding = get_embedding(expanded_text)
        print(f"✅ Expanded query embedding: {len(expanded_embedding)} dims")
        
        # Test against target contents
        print(f"\n📊 Similarity Scores:")
        print("Target Content | Raw Query | Expanded Query")
        print("-" * 50)
        
        for target in target_contents:
            target_embedding = get_embedding(target)
            
            raw_similarity = cosine_similarity(raw_embedding, target_embedding)
            expanded_similarity = cosine_similarity(expanded_embedding, target_embedding)
            
            improvement = expanded_similarity - raw_similarity
            improvement_str = f"(+{improvement:.3f})" if improvement > 0 else f"({improvement:.3f})"
            
            print(f"{target[:30]:<30} | {raw_similarity:.3f}     | {expanded_similarity:.3f} {improvement_str}")
        
        print()

def test_expansion_strategies():
    """Test different ways to combine query with expanded terms"""
    print("\n🎯 Testing Expansion Strategies...")
    
    query = "memory compression crisis"
    expanded_terms = ["data compression failure", "storage optimization issues", "system memory overload", "resource constraints", "context window overflow"]
    
    print(f"Base query: '{query}'")
    print(f"Expanded terms: {expanded_terms}")
    
    # Strategy 1: Query only
    strategy1 = query
    embed1 = get_embedding(strategy1)
    
    # Strategy 2: Query + expanded terms (simple concatenation)  
    strategy2 = query + " " + " ".join(expanded_terms)
    embed2 = get_embedding(strategy2)
    
    # Strategy 3: Expanded terms only
    strategy3 = " ".join(expanded_terms)
    embed3 = get_embedding(strategy3)
    
    # Strategy 4: Query repeated + expanded terms
    strategy4 = f"{query} {query} " + " ".join(expanded_terms)
    embed4 = get_embedding(strategy4)
    
    # Test against a target
    target = "450 memories creating context window overflow causing AI agent resource exhaustion and system termination"
    target_embed = get_embedding(target)
    
    strategies = [
        ("Query Only", embed1),
        ("Query + Expanded", embed2), 
        ("Expanded Only", embed3),
        ("Query Weighted + Expanded", embed4)
    ]
    
    print(f"\nTarget: {target[:60]}...")
    print("\nStrategy Comparison:")
    for name, embedding in strategies:
        similarity = cosine_similarity(embedding, target_embed)
        print(f"{name:<25}: {similarity:.3f}")

def main():
    test_query_embedding_approaches()
    test_expansion_strategies()
    print("\n🎉 Expansion testing completed!")

if __name__ == "__main__":
    main()