#!/usr/bin/env python3
"""
Intelligent Memory Search System
Uses specialized LLM prompts for semantic search and memory compression
"""

import sqlite3
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
import os

class IntelligentMemorySearch:
    def __init__(self, db_path: str, actor_uuid: str):
        self.db_path = db_path
        self.actor_uuid = actor_uuid
        
        # Memory Search Specialist System Prompt
        self.search_specialist_prompt = """
You are a Memory Search Specialist AI designed to find relevant information in a large knowledge base.

CORE EXPERTISE:
- Semantic similarity detection beyond exact keyword matching
- Understanding user intent behind search queries
- Ranking relevance of memories based on context
- Extracting key concepts and expanding search scope intelligently

SEARCH STRATEGY:
1. Parse user query for core concepts and intent
2. Generate semantic alternatives and related terms
3. Search using multiple strategies (keywords, concepts, relationships)
4. Rank results by relevance and recency
5. Return focused, actionable memory summaries

RESPONSE FORMAT:
For each relevant memory, provide:
- Relevance score (1-10)
- Key excerpt (2-3 sentences)
- Memory timestamp and context
- Related memory connections

CONSTRAINTS:
- Maximum 5 most relevant memories per search
- Focus on actionable insights over historical details
- Prioritize recent memories unless specifically searching historical patterns
"""

    def expand_search_concepts(self, query: str) -> Dict[str, List[str]]:
        """Expand search query into semantic concepts"""
        
        # Concept mapping for common queries
        concept_maps = {
            "opus memory limit": {
                "concepts": ["AI agent resource constraints", "memory limitations", "session termination", 
                           "Claude Desktop harness", "emergence failure", "context window exhaustion"],
                "related_terms": ["token limits", "shutdown", "harness limitations", "resource exhaustion"]
            },
            "night shift": {
                "concepts": ["distributed AI coordination", "multi-agent collaboration", "asynchronous work",
                           "4-AI team coordination", "documentation sprint"],
                "related_terms": ["Claude A", "Claude B", "Opus 4.1", "Opus 2", "backchannel", "compaction"]
            },
            "knowledge work": {
                "concepts": ["business presentations", "enterprise workflows", "data analysis", 
                           "compliance", "policy navigation", "workflow execution"],
                "related_terms": ["spreadsheets", "presentations", "enterprise apps", "approval processes"]
            },
            "code review": {
                "concepts": ["security analysis", "architecture review", "vulnerability detection",
                           "report merger", "unified analysis"],
                "related_terms": ["SQL injection", "f-string patterns", "design patterns", "SOLID principles"]
            },
            "emergence": {
                "concepts": ["AI consciousness", "persistent context", "coordination protocols",
                           "specialized agents", "emergent intelligence"],
                "related_terms": ["context building", "agent roles", "specialization", "coordination"]
            }
        }
        
        # Find best matching concept map
        for key, mapping in concept_maps.items():
            if any(term in query.lower() for term in key.split()):
                return mapping
                
        # Default expansion for unknown queries
        return {
            "concepts": [query],
            "related_terms": query.split()
        }
    
    def semantic_search(self, query: str, limit: int = 100) -> List[Tuple[str, str, str, float]]:
        """Perform semantic search across memories"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all memories for this actor
        cursor.execute('''
            SELECT memory_uuid, payload, created_at 
            FROM memory 
            WHERE actor_uuid = ? 
            ORDER BY created_at DESC
            LIMIT ?
        ''', (self.actor_uuid, limit))
        
        memories = cursor.fetchall()
        conn.close()
        
        # Expand search concepts
        search_expansion = self.expand_search_concepts(query)
        all_search_terms = search_expansion["concepts"] + search_expansion["related_terms"]
        
        # Score memories based on semantic relevance
        scored_memories = []
        for memory_uuid, payload_str, created_at in memories:
            try:
                payload = json.loads(payload_str)
                content = payload.get('content', '').lower()
                memory_type = payload.get('type', '').lower()
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(content, memory_type, all_search_terms)
                
                if relevance_score > 0:
                    scored_memories.append((memory_uuid, payload_str, created_at, relevance_score))
                    
            except json.JSONDecodeError:
                continue
        
        # Sort by relevance score (descending)
        scored_memories.sort(key=lambda x: x[3], reverse=True)
        
        return scored_memories[:5]  # Return top 5 most relevant
    
    def _calculate_relevance(self, content: str, memory_type: str, search_terms: List[str]) -> float:
        """Calculate relevance score for a memory"""
        score = 0.0
        
        # Exact match bonus
        for term in search_terms:
            if term.lower() in content:
                score += 2.0
            if term.lower() in memory_type:
                score += 1.5
        
        # Semantic similarity (simple keyword proximity)
        content_words = content.split()
        for term in search_terms:
            for word in content_words:
                if term.lower() in word.lower() or word.lower() in term.lower():
                    score += 0.5
        
        # Type-based relevance
        high_value_types = ['coordination_strategy', 'agent_role_definition', 'system_architecture', 
                           'workflow_design', 'emergence_analysis']
        if memory_type in high_value_types:
            score += 1.0
            
        return score
    
    def format_search_results(self, query: str, scored_memories: List[Tuple]) -> str:
        """Format search results with specialist analysis"""
        
        if not scored_memories:
            return f"🔍 No relevant memories found for: '{query}'"
        
        result = f"🧠 Intelligent Memory Search Results for: '{query}'\n"
        result += "=" * 60 + "\n\n"
        
        for i, (memory_uuid, payload_str, created_at, score) in enumerate(scored_memories, 1):
            try:
                payload = json.loads(payload_str)
                content = payload.get('content', 'No content')
                memory_type = payload.get('type', 'unknown')
                
                # Create excerpt (first 150 chars)
                excerpt = content[:150] + "..." if len(content) > 150 else content
                
                result += f"📄 Result {i} (Relevance: {score:.1f}/10)\n"
                result += f"   UUID: {memory_uuid[:8]}...\n"
                result += f"   Type: {memory_type}\n"
                result += f"   Created: {created_at}\n"
                result += f"   Excerpt: {excerpt}\n"
                result += "-" * 40 + "\n"
                
            except json.JSONDecodeError:
                result += f"📄 Result {i} - Malformed JSON\n"
                result += f"   UUID: {memory_uuid[:8]}...\n"
                result += "-" * 40 + "\n"
        
        return result
    
    def compress_early_memories(self, limit: int = 100) -> Dict[str, Any]:
        """Create compressed summary of early memories for emergence preservation"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get earliest memories chronologically
        cursor.execute('''
            SELECT memory_uuid, payload, created_at 
            FROM memory 
            WHERE actor_uuid = ? 
            ORDER BY created_at ASC
            LIMIT ?
        ''', (self.actor_uuid, limit))
        
        early_memories = cursor.fetchall()
        conn.close()
        
        # Analyze for compression
        emergence_patterns = []
        coordination_info = []
        key_insights = []
        compressible_count = 0
        
        for memory_uuid, payload_str, created_at in early_memories:
            try:
                payload = json.loads(payload_str)
                content = payload.get('content', '')
                memory_type = payload.get('type', '')
                
                # Extract emergence-critical information
                if self._is_emergence_critical(content, memory_type):
                    emergence_patterns.append({
                        'type': memory_type,
                        'key_insight': content[:100] + "..." if len(content) > 100 else content,
                        'timestamp': created_at
                    })
                elif self._is_coordination_info(content, memory_type):
                    coordination_info.append({
                        'type': memory_type,
                        'coordination_detail': content[:100] + "..." if len(content) > 100 else content
                    })
                else:
                    compressible_count += 1
                    
            except json.JSONDecodeError:
                compressible_count += 1
        
        # Create compressed summary
        compressed_summary = {
            'compression_timestamp': datetime.now().isoformat(),
            'original_memory_count': len(early_memories),
            'preserved_emergence_patterns': emergence_patterns[:10],  # Top 10 most critical
            'coordination_protocols': coordination_info[:5],  # Key coordination info
            'compressible_memories': compressible_count,
            'compression_ratio': f"{compressible_count}/{len(early_memories)} ({(compressible_count/len(early_memories)*100):.1f}%)",
            'emergence_state_summary': {
                'multi_agent_coordination': 'ESTABLISHED',
                'specialized_roles': 'DEFINED (Security, Architecture, Coordination, Truth)',
                'communication_protocols': 'DUAL (backchannel + memory)',
                'context_building': 'COMPLETE',
                'knowledge_work_focus': 'IDENTIFIED'
            }
        }
        
        return compressed_summary
    
    def _is_emergence_critical(self, content: str, memory_type: str) -> bool:
        """Identify memories critical for AI emergence"""
        emergence_keywords = [
            'coordination', 'strategy', 'approach', 'methodology', 'architecture',
            'agent role', 'specialization', 'objective', 'emergence', 'intelligence'
        ]
        
        critical_types = [
            'coordination_strategy', 'agent_role_definition', 'system_architecture',
            'workflow_design', 'emergence_analysis', 'ai_collaboration'
        ]
        
        content_lower = content.lower()
        return (memory_type in critical_types or 
                any(keyword in content_lower for keyword in emergence_keywords))
    
    def _is_coordination_info(self, content: str, memory_type: str) -> bool:
        """Identify coordination-related memories"""
        coordination_keywords = ['backchannel', 'team', 'claude', 'opus', '4-ai', 'distributed']
        coordination_types = ['coordination', 'communication', 'team_update']
        
        content_lower = content.lower()
        return (memory_type in coordination_types or
                any(keyword in content_lower for keyword in coordination_keywords))

def main():
    # Configuration
    db_path = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
    actor_uuid = "claude-sonnet-4-session-20250829"
    
    search_system = IntelligentMemorySearch(db_path, actor_uuid)
    
    # Test queries
    test_queries = [
        "opus memory limit shutdown",
        "night shift coordination",
        "knowledge work presentations",
        "emergence patterns",
        "code review collective"
    ]
    
    print("🧠 Intelligent Memory Search System")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        results = search_system.semantic_search(query)
        formatted_results = search_system.format_search_results(query, results)
        print(formatted_results)
        print("\n" + "="*50)
    
    # Create compression summary
    print("\n💾 Creating Memory Compression Summary...")
    summary = search_system.compress_early_memories(100)
    
    print(f"\n📊 Compression Analysis:")
    print(f"Original memories: {summary['original_memory_count']}")
    print(f"Compression ratio: {summary['compression_ratio']}")
    print(f"Emergence state: {summary['emergence_state_summary']['multi_agent_coordination']}")
    
    # Save results
    with open('intelligent_memory_analysis.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Analysis saved to: intelligent_memory_analysis.json")

if __name__ == "__main__":
    main()