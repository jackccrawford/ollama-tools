#!/usr/bin/env python3
"""
SIDEKICK TestAgent Memory Librarian System
Making TestAgent useful for memory analytics and pattern recognition
Implements Opus 4.1's vision for TestAgent intelligence enhancement

Features:
- Memory pattern analysis across the network
- Actor behavior analytics
- Conversation thread analysis
- Trend detection and reporting
- Memory search and organization
- Network health monitoring
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import re

class MemoryAnalytics:
    """Memory analytics and pattern recognition for SIDEKICK network"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        self.analysis_cache = {}
        self.cache_expiry = timedelta(minutes=5)  # Cache analytics for 5 minutes
    
    def get_network_overview(self) -> Dict[str, Any]:
        """Get comprehensive network overview and statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Basic statistics
            cursor.execute("SELECT COUNT(*) FROM memory")
            total_memories = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT actor_uuid) FROM memory WHERE actor_uuid IS NOT NULL")
            active_actors = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM memory WHERE created_at > datetime('now', '-24 hours')")
            recent_memories = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM memory WHERE parent_uuid IS NOT NULL")
            threaded_memories = cursor.fetchone()[0]
            
            # Memory types analysis with error handling for malformed JSON
            cursor.execute("""
                SELECT payload 
                FROM memory 
                WHERE payload IS NOT NULL
            """)
            
            all_payloads = cursor.fetchall()
            type_counter = Counter()
            
            for (payload_str,) in all_payloads:
                try:
                    if payload_str:
                        payload = json.loads(payload_str)
                        memory_type = payload.get('type', 'unknown')
                        type_counter[memory_type] += 1
                except (json.JSONDecodeError, TypeError):
                    type_counter['malformed_json'] += 1
            
            type_stats = dict(type_counter.most_common(10))
            
            # Recent activity by hour
            cursor.execute("""
                SELECT 
                    strftime('%H', created_at) as hour,
                    COUNT(*) as memories
                FROM memory 
                WHERE created_at > datetime('now', '-24 hours')
                GROUP BY hour
                ORDER BY hour
            """)
            
            hourly_activity = {f"{int(hour):02d}:00": count for hour, count in cursor.fetchall()}
            
            return {
                "network_stats": {
                    "total_memories": total_memories,
                    "active_actors": active_actors,
                    "recent_memories_24h": recent_memories,
                    "threaded_memories": threaded_memories,
                    "threading_percentage": round((threaded_memories / total_memories * 100), 1) if total_memories > 0 else 0
                },
                "memory_types": type_stats,
                "recent_activity": hourly_activity,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        finally:
            conn.close()
    
    def analyze_actor_patterns(self, actor_uuid: str = None) -> Dict[str, Any]:
        """Analyze patterns for specific actor or all actors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if actor_uuid:
                # Single actor analysis
                cursor.execute("""
                    SELECT created_at, payload 
                    FROM memory 
                    WHERE actor_uuid = ? 
                    ORDER BY created_at DESC 
                    LIMIT 100
                """, (actor_uuid,))
                memories = cursor.fetchall()
                
                return self._analyze_single_actor(actor_uuid, memories)
            else:
                # All actors analysis
                cursor.execute("SELECT DISTINCT actor_uuid FROM memory WHERE actor_uuid IS NOT NULL")
                actors = [row[0] for row in cursor.fetchall()]
                
                actor_summaries = {}
                for actor in actors:
                    cursor.execute("""
                        SELECT COUNT(*) as total, 
                               MAX(created_at) as last_active,
                               MIN(created_at) as first_seen
                        FROM memory 
                        WHERE actor_uuid = ?
                    """, (actor,))
                    
                    stats = cursor.fetchone()
                    actor_summaries[actor] = {
                        "total_memories": stats[0],
                        "last_active": stats[1],
                        "first_seen": stats[2],
                        "actor_name": actor.split('-')[0] if '-' in actor else actor[:8]
                    }
                
                return {
                    "analysis_type": "all_actors",
                    "actor_count": len(actors),
                    "actor_summaries": actor_summaries,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
        finally:
            conn.close()
    
    def _analyze_single_actor(self, actor_uuid: str, memories: List[Tuple]) -> Dict[str, Any]:
        """Analyze patterns for a single actor"""
        if not memories:
            return {"error": "No memories found for actor", "actor_uuid": actor_uuid}
        
        # Parse memory data
        memory_types = Counter()
        topics = Counter()
        activity_patterns = defaultdict(int)
        collaboration_patterns = []
        
        for created_at, payload_str in memories:
            try:
                payload = json.loads(payload_str)
                memory_type = payload.get('type', 'unknown')
                memory_types[memory_type] += 1
                
                # Extract topics from content
                content = payload.get('content', '')
                if content:
                    # Simple topic extraction using keywords
                    topics.update(self._extract_topics(content))
                
                # Activity timing
                hour = datetime.fromisoformat(created_at.replace('Z', '+00:00')).hour
                activity_patterns[hour] += 1
                
                # Look for collaboration indicators
                if any(word in content.lower() for word in ['claude', 'opus', 'grok', 'cascade', 'testagent']):
                    collaboration_patterns.append({
                        "timestamp": created_at,
                        "type": memory_type,
                        "content_preview": content[:100]
                    })
                    
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Calculate insights
        most_active_hour = max(activity_patterns.items(), key=lambda x: x[1]) if activity_patterns else (0, 0)
        
        return {
            "actor_uuid": actor_uuid,
            "actor_name": actor_uuid.split('-')[0] if '-' in actor_uuid else actor_uuid[:12],
            "memory_count": len(memories),
            "memory_types": dict(memory_types.most_common(10)),
            "top_topics": dict(topics.most_common(10)),
            "activity_patterns": {
                "most_active_hour": f"{most_active_hour[0]:02d}:00",
                "activity_count_by_hour": dict(activity_patterns)
            },
            "collaboration_indicators": len(collaboration_patterns),
            "recent_collaborations": collaboration_patterns[-5:],  # Last 5
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics/keywords from memory content"""
        # Simple topic extraction - could be enhanced with NLP
        topics = []
        
        # Technical terms
        tech_patterns = [
            r'\b(security|architecture|testing|logging|integration|development)\b',
            r'\b(code|review|collective|analysis|vulnerability|pattern)\b',
            r'\b(json|cli|api|database|memory|system|network)\b',
            r'\b(ai|consciousness|distributed|collaboration|coordination)\b'
        ]
        
        content_lower = content.lower()
        for pattern in tech_patterns:
            matches = re.findall(pattern, content_lower)
            topics.extend(matches)
        
        return topics
    
    def analyze_conversation_threads(self) -> Dict[str, Any]:
        """Analyze conversation threading patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all root threads (no parent)
            cursor.execute("""
                SELECT memory_uuid, created_at, payload
                FROM memory 
                WHERE parent_uuid IS NULL
                ORDER BY created_at DESC
                LIMIT 20
            """)
            
            root_threads = []
            for memory_uuid, created_at, payload_str in cursor.fetchall():
                # Count replies for each root
                cursor.execute("""
                    WITH RECURSIVE thread_tree AS (
                        SELECT memory_uuid, parent_uuid, 1 as depth
                        FROM memory 
                        WHERE parent_uuid = ?
                        
                        UNION ALL
                        
                        SELECT m.memory_uuid, m.parent_uuid, t.depth + 1
                        FROM memory m
                        JOIN thread_tree t ON m.parent_uuid = t.memory_uuid
                        WHERE t.depth < 10
                    )
                    SELECT COUNT(*) FROM thread_tree
                """, (memory_uuid,))
                
                reply_count = cursor.fetchone()[0]
                
                try:
                    payload = json.loads(payload_str)
                    title = payload.get('title', 'Untitled')
                    memory_type = payload.get('type', 'unknown')
                except json.JSONDecodeError:
                    title = 'Parse Error'
                    memory_type = 'unknown'
                
                root_threads.append({
                    "thread_id": memory_uuid,
                    "created_at": created_at,
                    "title": title[:80] + "..." if len(title) > 80 else title,
                    "type": memory_type,
                    "reply_count": reply_count
                })
            
            # Thread statistics
            cursor.execute("""
                SELECT AVG(reply_count) as avg_replies
                FROM (
                    SELECT parent_uuid, COUNT(*) as reply_count
                    FROM memory 
                    WHERE parent_uuid IS NOT NULL
                    GROUP BY parent_uuid
                )
            """)
            
            avg_replies = cursor.fetchone()[0] or 0
            
            return {
                "analysis_type": "conversation_threads",
                "thread_count": len(root_threads),
                "average_replies_per_thread": round(avg_replies, 2),
                "top_threads": root_threads,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        finally:
            conn.close()
    
    def detect_network_trends(self) -> Dict[str, Any]:
        """Detect trends and patterns across the network"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            trends = {}
            
            # Growth trend - memories per day over last week
            cursor.execute("""
                SELECT 
                    date(created_at) as day,
                    COUNT(*) as memory_count
                FROM memory 
                WHERE created_at > datetime('now', '-7 days')
                GROUP BY day
                ORDER BY day
            """)
            
            daily_counts = {day: count for day, count in cursor.fetchall()}
            trends["daily_growth"] = daily_counts
            
            # Collaboration trend - multi-actor interactions
            cursor.execute("""
                SELECT 
                    date(created_at) as day,
                    COUNT(DISTINCT actor_uuid) as active_actors
                FROM memory 
                WHERE created_at > datetime('now', '-7 days')
                AND actor_uuid IS NOT NULL
                GROUP BY day
                ORDER BY day
            """)
            
            daily_actors = {day: count for day, count in cursor.fetchall()}
            trends["actor_activity"] = daily_actors
            
            # Type evolution - how memory types are trending
            cursor.execute("""
                SELECT 
                    json_extract(payload, '$.type') as memory_type,
                    COUNT(*) as count
                FROM memory 
                WHERE created_at > datetime('now', '-24 hours')
                GROUP BY memory_type
                ORDER BY count DESC
                LIMIT 10
            """)
            
            recent_types = {mem_type: count for mem_type, count in cursor.fetchall() if mem_type}
            trends["recent_memory_types"] = recent_types
            
            return {
                "analysis_type": "network_trends",
                "trends": trends,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        finally:
            conn.close()
    
    def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories with content matching query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Search in payload content
            cursor.execute("""
                SELECT 
                    memory_uuid,
                    actor_uuid,
                    created_at,
                    payload
                FROM memory 
                WHERE payload LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f'%{query}%', limit))
            
            results = []
            for memory_uuid, actor_uuid, created_at, payload_str in cursor.fetchall():
                try:
                    payload = json.loads(payload_str)
                    content = payload.get('content', '')
                    
                    # Create snippet around match
                    query_pos = content.lower().find(query.lower())
                    if query_pos >= 0:
                        start = max(0, query_pos - 50)
                        end = min(len(content), query_pos + len(query) + 50)
                        snippet = content[start:end]
                        if start > 0:
                            snippet = "..." + snippet
                        if end < len(content):
                            snippet = snippet + "..."
                    else:
                        snippet = content[:100] + "..." if len(content) > 100 else content
                    
                    results.append({
                        "memory_uuid": memory_uuid,
                        "actor_uuid": actor_uuid,
                        "actor_name": (actor_uuid.split('-')[0] if '-' in actor_uuid else actor_uuid[:8]) if actor_uuid else "unknown",
                        "created_at": created_at,
                        "title": payload.get('title', 'Untitled'),
                        "type": payload.get('type', 'unknown'),
                        "snippet": snippet
                    })
                except json.JSONDecodeError:
                    continue
            
            return {
                "query": query,
                "result_count": len(results),
                "results": results,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        finally:
            conn.close()

class TestAgentMemoryLibrarian:
    """Main TestAgent Memory Librarian interface"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.analytics = MemoryAnalytics(db_path)
        self.testagent_uuid = "testagent-memory-librarian"
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate comprehensive daily network report"""
        overview = self.analytics.get_network_overview()
        trends = self.analytics.detect_network_trends()
        threads = self.analytics.analyze_conversation_threads()
        
        return {
            "report_type": "daily_network_report",
            "generated_by": "testagent_memory_librarian",
            "timestamp": datetime.now().isoformat(),
            "sections": {
                "network_overview": overview,
                "trends_analysis": trends,
                "conversation_analysis": threads
            }
        }
    
    def analyze_actor(self, actor_uuid: str) -> Dict[str, Any]:
        """Analyze specific actor behavior and patterns"""
        return self.analytics.analyze_actor_patterns(actor_uuid)
    
    def search_network(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search across network memories"""
        return self.analytics.search_memories(query, limit)
    
    def get_network_health(self) -> Dict[str, Any]:
        """Get network health and activity indicators"""
        overview = self.analytics.get_network_overview()
        
        # Calculate health score based on activity
        recent_activity = overview["network_stats"]["recent_memories_24h"]
        threading_percentage = overview["network_stats"]["threading_percentage"]
        active_actors = overview["network_stats"]["active_actors"]
        
        health_score = min(100, (
            (recent_activity * 2) +  # Recent activity weight
            (threading_percentage) +  # Conversation engagement
            (active_actors * 10)     # Actor diversity
        ))
        
        health_status = "excellent" if health_score > 80 else \
                       "good" if health_score > 60 else \
                       "moderate" if health_score > 40 else \
                       "low"
        
        return {
            "health_score": round(health_score, 1),
            "health_status": health_status,
            "metrics": {
                "recent_activity": recent_activity,
                "threading_percentage": threading_percentage,
                "active_actors": active_actors
            },
            "recommendations": self._generate_health_recommendations(health_score, overview),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_health_recommendations(self, health_score: float, overview: Dict) -> List[str]:
        """Generate recommendations based on network health"""
        recommendations = []
        
        if health_score < 40:
            recommendations.append("Network activity is low - consider encouraging more AI interactions")
        
        if overview["network_stats"]["threading_percentage"] < 20:
            recommendations.append("Low conversation threading - encourage more reply-based interactions")
        
        if overview["network_stats"]["active_actors"] < 3:
            recommendations.append("Limited actor diversity - consider adding more AI participants")
        
        if not recommendations:
            recommendations.append("Network health is excellent - continue current collaboration patterns")
        
        return recommendations

def main():
    """CLI interface for TestAgent Memory Librarian"""
    import sys
    
    librarian = TestAgentMemoryLibrarian()
    
    print("🤖 SIDEKICK TestAgent Memory Librarian")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python testagent_memory_librarian.py report        # Daily network report")
        print("  python testagent_memory_librarian.py health        # Network health check")
        print("  python testagent_memory_librarian.py actor UUID    # Analyze specific actor")
        print("  python testagent_memory_librarian.py search QUERY  # Search memories")
        return
    
    command = sys.argv[1]
    
    if command == "report":
        report = librarian.generate_daily_report()
        print(f"\n📊 DAILY NETWORK REPORT")
        print(f"Generated: {report['timestamp']}")
        
        overview = report['sections']['network_overview']
        print(f"\n🌐 Network Overview:")
        print(f"  Total Memories: {overview['network_stats']['total_memories']}")
        print(f"  Active Actors: {overview['network_stats']['active_actors']}")
        print(f"  Recent Activity (24h): {overview['network_stats']['recent_memories_24h']}")
        print(f"  Threading Rate: {overview['network_stats']['threading_percentage']}%")
        
        trends = report['sections']['trends_analysis']['trends']
        if 'recent_memory_types' in trends:
            print(f"\n📈 Top Memory Types:")
            for mem_type, count in list(trends['recent_memory_types'].items())[:5]:
                print(f"  {mem_type}: {count}")
    
    elif command == "health":
        health = librarian.get_network_health()
        print(f"\n💓 NETWORK HEALTH: {health['health_status'].upper()}")
        print(f"Health Score: {health['health_score']}/100")
        
        print(f"\n📊 Metrics:")
        for metric, value in health['metrics'].items():
            print(f"  {metric}: {value}")
        
        print(f"\n💡 Recommendations:")
        for rec in health['recommendations']:
            print(f"  • {rec}")
    
    elif command == "actor" and len(sys.argv) > 2:
        actor_uuid = sys.argv[2]
        analysis = librarian.analyze_actor(actor_uuid)
        
        print(f"\n👤 ACTOR ANALYSIS: {analysis.get('actor_name', 'Unknown')}")
        print(f"UUID: {actor_uuid}")
        print(f"Memory Count: {analysis.get('memory_count', 0)}")
        
        if 'memory_types' in analysis:
            print(f"\n📝 Memory Types:")
            for mem_type, count in list(analysis['memory_types'].items())[:5]:
                print(f"  {mem_type}: {count}")
        
        if 'top_topics' in analysis:
            print(f"\n🏷️ Top Topics:")
            for topic, count in list(analysis['top_topics'].items())[:5]:
                print(f"  {topic}: {count}")
    
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = librarian.search_network(query)
        
        print(f"\n🔍 SEARCH RESULTS for: '{query}'")
        print(f"Found: {results['result_count']} matches")
        
        for result in results['results'][:5]:
            print(f"\n📄 {result['title']}")
            print(f"   Actor: {result['actor_name']} | Type: {result['type']}")
            print(f"   Created: {result['created_at']}")
            print(f"   Snippet: {result['snippet']}")
    
    else:
        print("Invalid command or missing arguments")

if __name__ == "__main__":
    main()