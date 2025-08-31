#!/usr/bin/env python3
"""
SIDEKICK Actor Logger System
Implements individual actor logs as proposed by Opus 4.1
Each actor writes to their own log file for better organization and debugging
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class ActorLogger:
    """Individual logging system for SIDEKICK actors"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        self.logs_dir = Path(__file__).parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
    def get_actor_log_path(self, actor_uuid: str) -> Path:
        """Get the log file path for a specific actor"""
        return self.logs_dir / f"{actor_uuid}.log"
    
    def log_memory(self, memory: Dict[str, Any], actor_uuid: str):
        """Log a memory creation event to the actor's individual log"""
        log_path = self.get_actor_log_path(actor_uuid)
        
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "event": "memory_created",
            "memory_uuid": memory.get("uuid"),
            "type": memory.get("type", "general_memory"),
            "preview": memory.get("content", "")[:100] + "..." if len(memory.get("content", "")) > 100 else memory.get("content", "")
        }
        
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_actor_activity(self, actor_uuid: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity for an actor from their log"""
        log_path = self.get_actor_log_path(actor_uuid)
        
        if not log_path.exists():
            return []
        
        activities = []
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    activities.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return activities
    
    def monitor_all_actors(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get recent activity for all actors"""
        actor_logs = {}
        
        for log_file in self.logs_dir.glob("*.log"):
            actor_uuid = log_file.stem
            actor_logs[actor_uuid] = self.get_actor_activity(actor_uuid, limit=5)
        
        return actor_logs
    
    def sync_from_database(self):
        """Sync existing memories from database to individual log files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all unique actors
        cursor.execute("SELECT DISTINCT actor_uuid FROM memory WHERE actor_uuid IS NOT NULL")
        actors = cursor.fetchall()
        
        for (actor_uuid,) in actors:
            # Get memories for this actor
            cursor.execute("""
                SELECT memory_uuid, created_at, payload 
                FROM memory 
                WHERE actor_uuid = ? 
                ORDER BY created_at
            """, (actor_uuid,))
            
            memories = cursor.fetchall()
            log_path = self.get_actor_log_path(actor_uuid)
            
            # Clear existing log and rebuild
            with open(log_path, 'w') as f:
                for memory_uuid, created_at, payload_str in memories:
                    try:
                        payload = json.loads(payload_str)
                        log_entry = {
                            "timestamp": created_at,
                            "event": "memory_created",
                            "memory_uuid": memory_uuid,
                            "type": payload.get("type", "general_memory"),
                            "preview": str(payload.get("content", ""))[:100] + "..."
                        }
                        f.write(json.dumps(log_entry) + "\n")
                    except json.JSONDecodeError:
                        continue
        
        conn.close()
        return len(actors)

def main():
    """Initialize and demonstrate the actor logger system"""
    logger = ActorLogger()
    
    print("🚀 SIDEKICK Actor Logger System")
    print("=" * 50)
    
    # Sync from existing database
    print("\n📊 Syncing from database...")
    actor_count = logger.sync_from_database()
    print(f"✅ Synced logs for {actor_count} actors")
    
    # Show activity summary
    print("\n📈 Recent Activity Summary:")
    all_activity = logger.monitor_all_actors()
    
    for actor_uuid, activities in all_activity.items():
        # Try to get actor name from database
        actor_name = actor_uuid[:8] + "..."  # Default to shortened UUID
        
        print(f"\n🤖 Actor: {actor_name} ({actor_uuid[:12]}...)")
        if activities:
            for activity in activities[-3:]:  # Show last 3 activities
                timestamp = activity.get('timestamp', 'unknown')
                preview = activity.get('preview', '')
                print(f"   • {timestamp}: {preview[:60]}...")
        else:
            print("   No recent activity")
    
    print("\n✨ Actor Logger System Ready!")
    print(f"📁 Log files location: {logger.logs_dir}")

if __name__ == "__main__":
    main()