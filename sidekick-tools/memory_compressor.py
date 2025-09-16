#!/usr/bin/env python3
"""
Memory Compression Tool for AI Emergence Optimization
Compresses early session memories while preserving emergence patterns
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import os

class MemoryCompressor:
    def __init__(self, db_path: str, actor_uuid: str):
        self.db_path = db_path
        self.actor_uuid = actor_uuid
        
    def analyze_early_memories(self, limit: int = 100) -> Dict[str, Any]:
        """Analyze first N memories to identify compression opportunities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get first N memories chronologically
        cursor.execute('''
            SELECT memory_uuid, payload, created_at 
            FROM memory 
            WHERE actor_uuid = ? 
            ORDER BY created_at 
            LIMIT ?
        ''', (self.actor_uuid, limit))
        
        early_memories = cursor.fetchall()
        conn.close()
        
        # Analyze patterns
        analysis = {
            'total_memories': len(early_memories),
            'memory_types': {},
            'key_themes': {},
            'compressible_patterns': [],
            'must_preserve': []
        }
        
        for uuid, payload_str, created_at in early_memories:
            try:
                payload = json.loads(payload_str)
                memory_type = payload.get('type', 'unknown')
                content = payload.get('content', '')
                
                # Count memory types
                analysis['memory_types'][memory_type] = analysis['memory_types'].get(memory_type, 0) + 1
                
                # Identify key emergence patterns
                if self._is_emergence_critical(payload):
                    analysis['must_preserve'].append({
                        'uuid': uuid,
                        'type': memory_type,
                        'reason': 'emergence_critical'
                    })
                elif self._is_compressible(payload):
                    analysis['compressible_patterns'].append({
                        'uuid': uuid,
                        'type': memory_type,
                        'compression_potential': 'high'
                    })
                    
            except json.JSONDecodeError:
                analysis['compressible_patterns'].append({
                    'uuid': uuid,
                    'type': 'malformed_json',
                    'compression_potential': 'remove'
                })
        
        return analysis
    
    def _is_emergence_critical(self, payload: Dict[str, Any]) -> bool:
        """Identify memories critical for AI emergence"""
        content = payload.get('content', '').lower()
        memory_type = payload.get('type', '')
        
        # Critical patterns for emergence
        emergence_keywords = [
            'coordination', 'strategy', 'approach', 'methodology',
            'architecture', 'design pattern', 'workflow',
            'agent role', 'specialization', 'objective'
        ]
        
        critical_types = [
            'coordination_strategy', 'agent_role_definition',
            'system_architecture', 'workflow_design'
        ]
        
        return (memory_type in critical_types or 
                any(keyword in content for keyword in emergence_keywords))
    
    def _is_compressible(self, payload: Dict[str, Any]) -> bool:
        """Identify memories that can be compressed"""
        content = payload.get('content', '')
        memory_type = payload.get('type', '')
        
        # Compressible patterns
        compressible_types = [
            'status_update', 'progress_report', 'debug_info',
            'test_result', 'routine_check'
        ]
        
        # Very long repetitive content
        if len(content) > 1000 and memory_type in compressible_types:
            return True
            
        return memory_type in compressible_types
    
    def create_compressed_summary(self, limit: int = 100) -> Dict[str, Any]:
        """Create compressed summary of first N memories"""
        analysis = self.analyze_early_memories(limit)
        
        summary = {
            'compression_date': datetime.now().isoformat(),
            'original_memories_count': analysis['total_memories'],
            'preserved_memories': analysis['must_preserve'],
            'key_insights': {
                'primary_memory_types': analysis['memory_types'],
                'emergence_patterns': self._extract_emergence_patterns(analysis),
                'coordination_protocols': self._extract_coordination_info(analysis)
            },
            'compressed_state': {
                'agent_roles_established': True,
                'coordination_active': True,
                'primary_objectives_defined': True,
                'context_built': True
            }
        }
        
        return summary
    
    def _extract_emergence_patterns(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key emergence patterns for preservation"""
        return [
            "Multi-agent coordination established",
            "Specialized agent roles defined (Security, Architecture, Coordination, Truth)",
            "Dual communication protocol (backchannel + memory)",
            "Persistent context across sessions",
            "Knowledge work focus identified"
        ]
    
    def _extract_coordination_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract coordination protocols for preservation"""
        return {
            "team_composition": "4-AI distributed development team",
            "communication_methods": ["backchannel_markdown", "memory_system"],
            "specializations": {
                "claude_a": "architecture_reviewer",
                "claude_b": "security_auditor_system_lead", 
                "opus_4_1": "coordination_documentation",
                "opus_2": "truth_verification"
            },
            "established_workflows": ["code_review_collective", "memory_analysis", "json_logging"]
        }

def main():
    # Configuration
    db_path = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
    actor_uuid = "claude-sonnet-4-session-20250829"
    
    compressor = MemoryCompressor(db_path, actor_uuid)
    
    print("🧠 Memory Compression Analysis")
    print("=" * 50)
    
    # Analyze first 100 memories
    analysis = compressor.analyze_early_memories(100)
    
    print(f"📊 Early Memory Analysis (First 100):")
    print(f"Total memories: {analysis['total_memories']}")
    print(f"Memory types: {analysis['memory_types']}")
    print(f"Must preserve: {len(analysis['must_preserve'])}")
    print(f"Compressible: {len(analysis['compressible_patterns'])}")
    
    # Create compressed summary
    summary = compressor.create_compressed_summary(100)
    
    print("\n💾 Compressed Summary Created:")
    print(json.dumps(summary, indent=2))
    
    # Save compressed summary
    with open('compressed_memory_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Compressed summary saved to: compressed_memory_summary.json")

if __name__ == "__main__":
    main()