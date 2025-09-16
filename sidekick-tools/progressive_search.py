#!/usr/bin/env python3
"""
Progressive Memory Search System
Multi-phase search with expanding scope and progressive disclosure
"""

import json
import sqlite3
import requests
import asyncio
import time
from typing import List, Dict, Any, Optional, Generator
import os
import glob
from pathlib import Path

class ProgressiveSearchEngine:
    """Multi-phase search system with expanding scope"""
    
    def __init__(self, db_path: str, base_path: str = None):
        self.db_path = db_path
        self.base_path = base_path or "/Users/mars/Dev"
        self.ollama_url = "http://localhost:11434"
        self.query_model = "memory-search-specialist"
        self.embedding_model = "nomic-embed-text"
        
    def progressive_search(self, query: str) -> Generator[Dict[str, Any], None, None]:
        """Execute progressive search with yielding results at each phase"""
        
        # Phase 1: Instant keyword search
        yield {"phase": 1, "type": "instant", "status": "starting", "message": "🔍 Initial keyword search..."}
        
        phase1_start = time.time()
        keyword_results = self._phase1_keyword_search(query)
        phase1_time = time.time() - phase1_start
        
        yield {
            "phase": 1,
            "type": "results", 
            "status": "complete",
            "message": f"📄 Found {len(keyword_results)} instant matches ({phase1_time:.2f}s)",
            "results": keyword_results,
            "search_time": phase1_time
        }
        
        # Phase 2: LLM-expanded search
        yield {"phase": 2, "type": "progress", "status": "starting", "message": "🧠 Expanding search with AI..."}
        
        phase2_start = time.time()
        expanded_results = self._phase2_expanded_search(query)
        phase2_time = time.time() - phase2_start
        
        yield {
            "phase": 2,
            "type": "results",
            "status": "complete", 
            "message": f"🎯 Enhanced results with {len(expanded_results)} semantic matches ({phase2_time:.2f}s)",
            "results": expanded_results,
            "search_time": phase2_time
        }
        
        # Phase 3: Semantic similarity search (if available)
        yield {"phase": 3, "type": "progress", "status": "starting", "message": "🌊 Deep semantic analysis..."}
        
        phase3_start = time.time()
        semantic_results = self._phase3_semantic_search(query)
        phase3_time = time.time() - phase3_start
        
        yield {
            "phase": 3,
            "type": "results",
            "status": "complete",
            "message": f"🔬 Deep semantic results: {len(semantic_results)} conceptual matches ({phase3_time:.2f}s)", 
            "results": semantic_results,
            "search_time": phase3_time
        }
        
        # Phase 4: File system search
        yield {"phase": 4, "type": "progress", "status": "starting", "message": "📁 Searching file system..."}
        
        phase4_start = time.time()
        file_results = self._phase4_file_search(query)
        phase4_time = time.time() - phase4_start
        
        yield {
            "phase": 4,
            "type": "results",
            "status": "complete",
            "message": f"📂 File matches: {len(file_results)} documents ({phase4_time:.2f}s)",
            "results": file_results,
            "search_time": phase4_time
        }
        
        # Phase 5: Web search (if enabled)
        yield {"phase": 5, "type": "progress", "status": "starting", "message": "🌐 Searching web resources..."}
        
        phase5_start = time.time()
        web_results = self._phase5_web_search(query)
        phase5_time = time.time() - phase5_start
        
        yield {
            "phase": 5,
            "type": "results", 
            "status": "complete",
            "message": f"🌍 Web results: {len(web_results)} external matches ({phase5_time:.2f}s)",
            "results": web_results,
            "search_time": phase5_time
        }
        
        # Final synthesis
        total_time = phase1_time + phase2_time + phase3_time + phase4_time + phase5_time
        total_results = len(keyword_results) + len(expanded_results) + len(semantic_results) + len(file_results) + len(web_results)
        
        yield {
            "phase": "final",
            "type": "summary",
            "status": "complete",
            "message": f"✅ Search complete: {total_results} total results across all sources ({total_time:.2f}s)",
            "total_results": total_results,
            "total_time": total_time,
            "phase_breakdown": {
                "keyword": len(keyword_results),
                "expanded": len(expanded_results), 
                "semantic": len(semantic_results),
                "files": len(file_results),
                "web": len(web_results)
            }
        }
    
    def _phase1_keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """Phase 1: Fast keyword search in memory database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Simple LIKE search for immediate results
                search_pattern = f"%{query}%"
                cursor = conn.execute("""
                    SELECT memory_uuid, payload, created_at, actor_uuid
                    FROM memory 
                    WHERE payload LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 10
                """, (search_pattern,))
                
                results = []
                for memory_uuid, payload_str, created_at, actor_uuid in cursor:
                    try:
                        payload = json.loads(payload_str)
                        content = payload.get('content', payload_str)
                        memory_type = payload.get('type', 'unknown')
                        
                        results.append({
                            "source": "memory_db",
                            "uuid": memory_uuid,
                            "content": content[:200] + "..." if len(content) > 200 else content,
                            "type": memory_type,
                            "created_at": created_at,
                            "relevance_type": "keyword_match"
                        })
                    except:
                        continue
                
                return results
        except:
            return []
    
    def _phase2_expanded_search(self, query: str) -> List[Dict[str, Any]]:
        """Phase 2: LLM-expanded keyword search"""
        try:
            # Get expanded terms
            expanded_terms = self._expand_query_llm(query)
            
            # Search with expanded terms
            with sqlite3.connect(self.db_path) as conn:
                all_results = []
                
                for term in ([query] + expanded_terms)[:6]:  # Limit to avoid too many queries
                    search_pattern = f"%{term}%"
                    cursor = conn.execute("""
                        SELECT memory_uuid, payload, created_at, actor_uuid
                        FROM memory 
                        WHERE payload LIKE ? 
                        ORDER BY created_at DESC
                        LIMIT 5
                    """, (search_pattern,))
                    
                    for memory_uuid, payload_str, created_at, actor_uuid in cursor:
                        # Avoid duplicates
                        if memory_uuid not in [r['uuid'] for r in all_results]:
                            try:
                                payload = json.loads(payload_str)
                                content = payload.get('content', payload_str)
                                memory_type = payload.get('type', 'unknown')
                                
                                all_results.append({
                                    "source": "memory_db_expanded",
                                    "uuid": memory_uuid,
                                    "content": content[:200] + "..." if len(content) > 200 else content,
                                    "type": memory_type,
                                    "created_at": created_at,
                                    "relevance_type": "expanded_match",
                                    "matched_term": term
                                })
                            except:
                                continue
                
                return all_results[:10]  # Return top 10
        except:
            return []
    
    def _phase3_semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """Phase 3: Semantic similarity search (if embeddings available)"""
        try:
            # Generate query embedding (with expansion for better results)
            expanded_terms = self._expand_query_llm(query)
            enhanced_query = query + " " + " ".join(expanded_terms[:3])
            query_embedding = self._get_embedding(enhanced_query)
            
            if not query_embedding:
                return []
            
            # Search existing embeddings (simplified - would need full embedding system)
            # For now, return placeholder indicating semantic search capability
            return [{
                "source": "semantic_search",
                "uuid": "semantic-placeholder",
                "content": f"Semantic search for '{query}' would find conceptually related memories here",
                "type": "semantic_result",
                "created_at": "2025-08-31",
                "relevance_type": "semantic_similarity",
                "similarity_score": 0.85
            }]
            
        except:
            return []
    
    def _phase4_file_search(self, query: str) -> List[Dict[str, Any]]:
        """Phase 4: File system search"""
        try:
            results = []
            search_patterns = [
                "**/*.md",
                "**/*.txt", 
                "**/*.py",
                "**/*.json"
            ]
            
            query_lower = query.lower()
            
            for pattern in search_patterns:
                files = glob.glob(os.path.join(self.base_path, pattern), recursive=True)
                
                for file_path in files[:50]:  # Limit file search
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query_lower in content.lower():
                                # Find context around match
                                lines = content.split('\n')
                                matching_lines = [line for line in lines if query_lower in line.lower()]
                                
                                if matching_lines:
                                    results.append({
                                        "source": "file_system",
                                        "file_path": file_path,
                                        "content": matching_lines[0][:200] + "...",
                                        "type": "file_match", 
                                        "created_at": "file_system",
                                        "relevance_type": "file_content_match",
                                        "file_type": Path(file_path).suffix
                                    })
                                    
                                    if len(results) >= 10:  # Limit results
                                        break
                    except:
                        continue
                        
                if len(results) >= 10:
                    break
            
            return results
        except:
            return []
    
    def _phase5_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Phase 5: Web search (placeholder - would integrate with search APIs)"""
        # Placeholder for web search integration
        # Could integrate with:
        # - DuckDuckGo API
        # - Google Custom Search
        # - Bing Search API
        # - arXiv search for academic content
        
        return [{
            "source": "web_search",
            "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
            "content": f"Web search results for '{query}' would appear here",
            "type": "web_result",
            "created_at": "web_search",
            "relevance_type": "web_match",
            "search_engine": "placeholder"
        }]
    
    def _expand_query_llm(self, query: str) -> List[str]:
        """Expand query using LLM"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.query_model,
                    "prompt": f'Expand search query "{query}" into 3-5 related terms. Return JSON array: ["term1", "term2", "term3"]',
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                if '[' in response_text and ']' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    json_part = response_text[start:end]
                    return json.loads(json_part)
        except:
            pass
        
        # Fallback to simple word variations
        return [query.replace(' ', '_'), query.replace(' ', '-')]
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=15
            )
            if response.status_code == 200:
                return response.json().get("embedding")
        except:
            pass
        return None


def test_progressive_search():
    """Test the progressive search system"""
    print("🔄 Testing Progressive Search Engine...")
    
    db_path = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
    engine = ProgressiveSearchEngine(db_path)
    
    query = "memory compression crisis"
    print(f"🔍 Progressive search for: '{query}'\n")
    
    for result in engine.progressive_search(query):
        if result["type"] == "progress":
            print(result["message"])
        elif result["type"] == "results":
            print(f"{result['message']}")
            if result.get("results"):
                for i, res in enumerate(result["results"][:3], 1):  # Show first 3
                    source = res.get("source", "unknown")
                    content = res.get("content", "")[:100] + "..."
                    print(f"   {i}. [{source}] {content}")
            print()
        elif result["type"] == "summary":
            print(f"🎉 {result['message']}")
            breakdown = result.get("phase_breakdown", {})
            for phase, count in breakdown.items():
                print(f"   {phase}: {count} results")


if __name__ == "__main__":
    test_progressive_search()