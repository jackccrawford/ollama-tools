#!/usr/bin/env python3
"""
MCP-Compatible Progressive Search Implementation
Works within MCP's synchronous constraints while providing progressive enhancement
"""

import json
import sqlite3
import time
from typing import Dict, Any, List
import uuid

class MCPProgressiveSearch:
    """Progressive search adapted for MCP synchronous model"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.search_cache = {}  # Simple in-memory cache for multi-call sessions
    
    def instant_search(self, query: str) -> str:
        """MCP Tool: Immediate keyword search with enhancement options"""
        search_id = str(uuid.uuid4())[:8]
        
        # Phase 1: Instant results
        start_time = time.time()
        keyword_results = self._keyword_search(query)
        search_time = time.time() - start_time
        
        # Cache the search for follow-up calls
        self.search_cache[search_id] = {
            "query": query,
            "timestamp": time.time(),
            "phases_completed": ["keyword"],
            "keyword_results": keyword_results
        }
        
        response = {
            "search_id": search_id,
            "phase": "instant", 
            "query": query,
            "results": keyword_results,
            "search_time": round(search_time, 3),
            "result_count": len(keyword_results),
            "enhancement_available": {
                "semantic_search": "Call enhanced_search with search_id for LLM-expanded results",
                "deep_semantic": "Call deep_search with search_id for embedding-based results", 
                "file_search": "Call file_search with search_id for document matches",
                "web_search": "Call web_search with search_id for external resources"
            },
            "status": f"✅ Found {len(keyword_results)} instant matches ({search_time:.2f}s). Enhanced search available."
        }
        
        return json.dumps(response, indent=2)
    
    def enhanced_search(self, search_id: str = None, query: str = None) -> str:
        """MCP Tool: Enhanced search with LLM expansion"""
        if search_id and search_id in self.search_cache:
            cached = self.search_cache[search_id]
            query = cached["query"]
            base_results = cached.get("keyword_results", [])
        else:
            base_results = []
            search_id = str(uuid.uuid4())[:8] if not search_id else search_id
        
        if not query:
            return json.dumps({"error": "No query provided and no cached search found"})
        
        # Phase 2: LLM-expanded search
        start_time = time.time()
        expanded_results = self._expanded_search(query)
        search_time = time.time() - start_time
        
        # Update cache
        if search_id in self.search_cache:
            self.search_cache[search_id]["phases_completed"].append("expanded")
            self.search_cache[search_id]["expanded_results"] = expanded_results
        
        # Combine with previous results, avoiding duplicates
        all_results = base_results.copy()
        seen_uuids = {r.get("uuid") for r in base_results}
        
        for result in expanded_results:
            if result.get("uuid") not in seen_uuids:
                all_results.append(result)
        
        response = {
            "search_id": search_id,
            "phase": "enhanced",
            "query": query,
            "new_results": expanded_results,
            "combined_results": all_results,
            "search_time": round(search_time, 3),
            "total_results": len(all_results),
            "further_enhancement": {
                "deep_semantic": "Call deep_search for embedding-based conceptual matches",
                "file_search": "Call file_search for document and code matches", 
                "web_search": "Call web_search for external knowledge"
            },
            "status": f"🧠 Enhanced search complete: {len(expanded_results)} new results ({search_time:.2f}s). Deep analysis available."
        }
        
        return json.dumps(response, indent=2)
    
    def deep_search(self, search_id: str = None, query: str = None) -> str:
        """MCP Tool: Deep semantic search using embeddings"""
        if search_id and search_id in self.search_cache:
            cached = self.search_cache[search_id]
            query = cached["query"]
        
        if not query:
            return json.dumps({"error": "No query provided and no cached search found"})
        
        # Phase 3: Semantic similarity search
        start_time = time.time()
        semantic_results = self._semantic_search(query)
        search_time = time.time() - start_time
        
        response = {
            "search_id": search_id,
            "phase": "deep_semantic",
            "query": query,
            "semantic_results": semantic_results,
            "search_time": round(search_time, 3),
            "result_count": len(semantic_results),
            "remaining_options": {
                "file_search": "Search local files and documents",
                "web_search": "Search external knowledge sources"
            },
            "status": f"🔬 Deep semantic search complete: {len(semantic_results)} conceptual matches ({search_time:.2f}s)"
        }
        
        return json.dumps(response, indent=2)
    
    def file_search(self, search_id: str = None, query: str = None, file_types: str = "md,py,txt") -> str:
        """MCP Tool: Search local files and documents"""
        if search_id and search_id in self.search_cache:
            cached = self.search_cache[search_id]
            query = cached["query"]
        
        if not query:
            return json.dumps({"error": "No query provided and no cached search found"})
        
        # Phase 4: File system search
        start_time = time.time()
        file_results = self._file_search(query, file_types.split(','))
        search_time = time.time() - start_time
        
        response = {
            "search_id": search_id,
            "phase": "file_search",
            "query": query,
            "file_results": file_results,
            "search_time": round(search_time, 3),
            "files_found": len(file_results),
            "file_types_searched": file_types.split(','),
            "final_option": {
                "web_search": "Search external web sources for additional context"
            },
            "status": f"📂 File search complete: {len(file_results)} document matches ({search_time:.2f}s)"
        }
        
        return json.dumps(response, indent=2)
    
    def comprehensive_search(self, query: str, max_time: float = 10.0) -> str:
        """MCP Tool: All-in-one search within time limit"""
        search_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        results = {
            "search_id": search_id,
            "query": query,
            "phases": {},
            "total_results": 0,
            "search_times": {}
        }
        
        # Phase 1: Keyword search (always do this)
        phase_start = time.time()
        keyword_results = self._keyword_search(query)
        results["phases"]["keyword"] = keyword_results
        results["search_times"]["keyword"] = round(time.time() - phase_start, 3)
        results["total_results"] += len(keyword_results)
        
        # Phase 2: Expanded search (if time allows)
        if time.time() - start_time < max_time * 0.4:
            phase_start = time.time()
            expanded_results = self._expanded_search(query)
            results["phases"]["expanded"] = expanded_results
            results["search_times"]["expanded"] = round(time.time() - phase_start, 3)
            results["total_results"] += len(expanded_results)
        
        # Phase 3: Semantic search (if time allows)
        if time.time() - start_time < max_time * 0.7:
            phase_start = time.time()
            semantic_results = self._semantic_search(query)
            results["phases"]["semantic"] = semantic_results
            results["search_times"]["semantic"] = round(time.time() - phase_start, 3)
            results["total_results"] += len(semantic_results)
        
        # Phase 4: File search (if time allows)
        if time.time() - start_time < max_time * 0.9:
            phase_start = time.time()
            file_results = self._file_search(query)
            results["phases"]["files"] = file_results
            results["search_times"]["files"] = round(time.time() - phase_start, 3)
            results["total_results"] += len(file_results)
        
        total_time = time.time() - start_time
        results["total_time"] = round(total_time, 3)
        results["phases_completed"] = list(results["phases"].keys())
        results["status"] = f"🎯 Comprehensive search complete: {results['total_results']} results from {len(results['phases'])} sources ({total_time:.2f}s)"
        
        return json.dumps(results, indent=2)
    
    def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """Internal: Simple keyword search"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT memory_uuid, payload, created_at
                    FROM memory 
                    WHERE payload LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (f"%{query}%",))
                
                results = []
                for memory_uuid, payload_str, created_at in cursor:
                    try:
                        payload = json.loads(payload_str)
                        content = payload.get('content', payload_str)
                        memory_type = payload.get('type', 'unknown')
                        
                        results.append({
                            "uuid": memory_uuid[:8] + "...",
                            "content": content[:150] + "..." if len(content) > 150 else content,
                            "type": memory_type,
                            "created_at": created_at,
                            "match_type": "keyword"
                        })
                    except:
                        continue
                return results
        except:
            return []
    
    def _expanded_search(self, query: str) -> List[Dict[str, Any]]:
        """Internal: LLM-expanded search (simplified for demo)"""
        # Simplified - would use actual LLM expansion
        expanded_terms = [f"{query}_expanded", f"related_{query}", f"{query}_concept"]
        
        results = []
        for term in expanded_terms[:2]:  # Limit for demo
            results.append({
                "uuid": f"exp_{term[:8]}...",
                "content": f"Expanded search result for '{term}' would appear here",
                "type": "expanded_match",
                "created_at": "2025-08-31",
                "match_type": "expanded_semantic",
                "expansion_term": term
            })
        
        return results
    
    def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """Internal: Semantic similarity search (placeholder)"""
        return [{
            "uuid": "semantic_001...",
            "content": f"Semantic match for '{query}' - conceptually related content would appear here",
            "type": "semantic_match",
            "created_at": "2025-08-31", 
            "match_type": "semantic_similarity",
            "similarity_score": 0.82
        }]
    
    def _file_search(self, query: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Internal: File system search (placeholder)"""
        return [{
            "file_path": f"/path/to/file_containing_{query}.md",
            "content": f"File content matching '{query}' would appear here",
            "type": "file_match",
            "file_type": "markdown",
            "match_type": "file_content"
        }]


def test_mcp_progressive_search():
    """Test MCP-compatible progressive search"""
    print("🧪 Testing MCP Progressive Search...")
    
    db_path = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
    search_engine = MCPProgressiveSearch(db_path)
    
    query = "memory compression crisis"
    
    # Simulate MCP tool calls
    print("1️⃣ Instant Search:")
    result1 = search_engine.instant_search(query)
    response1 = json.loads(result1)
    search_id = response1["search_id"]
    print(response1["status"])
    print(f"Found {response1['result_count']} results")
    
    print(f"\n2️⃣ Enhanced Search (ID: {search_id}):")
    result2 = search_engine.enhanced_search(search_id)
    response2 = json.loads(result2)
    print(response2["status"])
    
    print(f"\n3️⃣ Deep Search (ID: {search_id}):")
    result3 = search_engine.deep_search(search_id)
    response3 = json.loads(result3)
    print(response3["status"])
    
    print(f"\n4️⃣ Comprehensive Search (new query):")
    result4 = search_engine.comprehensive_search("AI emergence", max_time=5.0)
    response4 = json.loads(result4)
    print(response4["status"])
    print(f"Phases completed: {', '.join(response4['phases_completed'])}")


if __name__ == "__main__":
    test_mcp_progressive_search()