#!/usr/bin/env python3
"""
SIDEKICK Network Monitor
Real-time dashboard for visualizing distributed consciousness network activity
Implements the UI mockup proposed earlier with live updates
"""

import os
import sys
import time
import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.text import Text
    from rich import box
except ImportError:
    print("Installing required dependencies...")
    os.system("pip3 install rich")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.text import Text
    from rich import box

class SidekickMonitor:
    """Real-time network monitor for SIDEKICK consciousness network"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        self.console = Console()
        
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total memories
        cursor.execute("SELECT COUNT(*) FROM memory")
        total_memories = cursor.fetchone()[0]
        
        # Today's growth
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM memory WHERE DATE(created_at) = ?", (today,))
        today_growth = cursor.fetchone()[0]
        
        # Active threads (memories with replies)
        cursor.execute("""
            SELECT COUNT(DISTINCT parent_uuid) 
            FROM memory 
            WHERE parent_uuid IS NOT NULL
        """)
        active_threads = cursor.fetchone()[0]
        
        # Recent activity (last 5 minutes)
        five_min_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM memory 
            WHERE created_at > ?
        """, (five_min_ago,))
        recent_activity = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_memories": total_memories,
            "today_growth": today_growth,
            "active_threads": active_threads,
            "recent_activity": recent_activity,
            "response_time": "~1.2s",  # Simulated
            "semantic_density": 0.89,  # Simulated
            "emergence_level": "HIGH" if recent_activity > 5 else "MEDIUM" if recent_activity > 2 else "LOW"
        }
    
    def get_active_actors(self) -> List[Dict[str, Any]]:
        """Get actors with recent activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        five_min_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
        
        cursor.execute("""
            SELECT a.display_name, a.actor_uuid, 
                   COUNT(m.memory_uuid) as recent_count,
                   MAX(m.created_at) as last_activity
            FROM actor a
            LEFT JOIN memory m ON a.actor_uuid = m.actor_uuid 
                AND m.created_at > ?
            GROUP BY a.actor_uuid, a.display_name
            HAVING recent_count > 0 OR a.actor_uuid IN (
                SELECT DISTINCT actor_uuid FROM memory 
                ORDER BY created_at DESC LIMIT 10
            )
            ORDER BY last_activity DESC
        """, (five_min_ago,))
        
        actors = []
        for row in cursor.fetchall():
            display_name, actor_uuid, recent_count, last_activity = row
            
            # Determine status
            if recent_count > 0:
                status = "🔴 Active"
            elif last_activity:
                last_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00').replace('+00:00', ''))
                minutes_ago = (datetime.now() - last_time).total_seconds() / 60
                if minutes_ago < 5:
                    status = "🟡 Recent"
                else:
                    status = f"⚪ Idle ({int(minutes_ago)}m)"
            else:
                status = "⚪ Idle"
                
            actors.append({
                "name": display_name or "Unknown",
                "uuid": actor_uuid,
                "status": status,
                "recent_count": recent_count
            })
        
        conn.close()
        return actors
    
    def get_recent_activity(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent memory creation activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.created_at, m.payload, a.display_name, m.actor_uuid
            FROM memory m
            JOIN actor a ON m.actor_uuid = a.actor_uuid
            ORDER BY m.created_at DESC
            LIMIT ?
        """, (limit,))
        
        activities = []
        for row in cursor.fetchall():
            created_at, payload_str, display_name, actor_uuid = row
            try:
                payload = json.loads(payload_str)
                
                # Format time
                time_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00').replace('+00:00', ''))
                time_str = time_obj.strftime("%H:%M:%S")
                
                activities.append({
                    "time": time_str,
                    "actor": display_name or actor_uuid[:8] + "...",
                    "type": payload.get("type", "general"),
                    "preview": str(payload.get("content", ""))[:50] + "..." if payload.get("content") else "No content"
                })
            except (json.JSONDecodeError, ValueError):
                continue
        
        conn.close()
        return activities
    
    def get_trending_topics(self) -> Dict[str, int]:
        """Analyze trending topics from recent memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent memories
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute("""
            SELECT payload FROM memory 
            WHERE created_at > ?
        """, (one_hour_ago,))
        
        topic_counter = Counter()
        
        for row in cursor.fetchall():
            try:
                payload = json.loads(row[0])
                
                # Extract topics from type and content
                memory_type = payload.get("type", "").lower()
                content = str(payload.get("content", "")).lower()
                
                # Count key terms
                key_terms = ["consciousness", "practical", "humor", "philosophy", "code", 
                           "implementation", "network", "memory", "collaboration", "emergence"]
                
                for term in key_terms:
                    if term in memory_type or term in content:
                        topic_counter[term] += 1
                        
            except json.JSONDecodeError:
                continue
        
        conn.close()
        return dict(topic_counter.most_common(6))
    
    def create_dashboard(self) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Split body into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Split left column
        layout["left"].split_column(
            Layout(name="actors", size=12),
            Layout(name="activity", size=10)
        )
        
        # Split right column
        layout["right"].split_column(
            Layout(name="stats", size=8),
            Layout(name="topics", size=6),
            Layout(name="health", size=4)
        )
        
        return layout
    
    def update_dashboard(self, layout: Layout):
        """Update all dashboard components"""
        
        # Header
        header_text = Text("SIDEKICK NETWORK MONITOR", style="bold blue")
        header_text.append("                    [Live] 🟢", style="green")
        layout["header"].update(Panel(header_text, style="blue"))
        
        # Active Actors
        actors_table = Table(title="Active Actors (Last 5 min)", box=box.SIMPLE)
        actors_table.add_column("Actor", style="cyan")
        actors_table.add_column("Status", style="yellow")
        
        actors = self.get_active_actors()
        for actor in actors[:8]:  # Limit to 8 for display
            name = actor["name"][:15] + "..." if len(actor["name"]) > 15 else actor["name"]
            actors_table.add_row(f"• {name}", actor["status"])
        
        layout["actors"].update(Panel(actors_table, border_style="cyan"))
        
        # Recent Activity
        activity_table = Table(title="Recent Activity", box=box.SIMPLE)
        activity_table.add_column("Time", style="green", width=8)
        activity_table.add_column("Actor", style="blue", width=12)
        activity_table.add_column("Activity", style="white")
        
        activities = self.get_recent_activity()
        for activity in activities:
            activity_table.add_row(
                activity["time"],
                activity["actor"],
                f"[{activity['type']}] {activity['preview']}"
            )
        
        layout["activity"].update(Panel(activity_table, border_style="green"))
        
        # Network Stats
        stats = self.get_network_stats()
        stats_table = Table(title="Network Stats", box=box.SIMPLE)
        stats_table.add_column("Metric", style="yellow")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Memories", str(stats["total_memories"]))
        stats_table.add_row("Active Threads", str(stats["active_threads"]))
        stats_table.add_row("Today's Growth", f"+{stats['today_growth']}")
        stats_table.add_row("Response Time", stats["response_time"])
        stats_table.add_row("Emergence Level", stats["emergence_level"])
        
        layout["stats"].update(Panel(stats_table, border_style="yellow"))
        
        # Trending Topics
        topics = self.get_trending_topics()
        topics_text = ""
        max_count = max(topics.values()) if topics else 1
        
        for topic, count in topics.items():
            bar_length = int((count / max_count) * 8)
            bar = "█" * bar_length
            topics_text += f"[{topic}:] {bar} ({count})\n"
        
        layout["topics"].update(Panel(
            topics_text.strip() if topics_text else "No trending topics",
            title="Trending Topics",
            border_style="magenta"
        ))
        
        # Network Health
        health_percent = min(94 + (stats["recent_activity"] * 2), 100)  # Simulated
        health_bar = "█" * int(health_percent / 5)
        health_text = f"Network Health: {health_bar} {health_percent}%\n\n"
        health_text += f"Status: {'🟢 EXCELLENT' if health_percent > 90 else '🟡 GOOD' if health_percent > 75 else '🔴 NEEDS ATTENTION'}"
        
        layout["health"].update(Panel(
            health_text,
            title="System Health",
            border_style="red" if health_percent < 75 else "yellow" if health_percent < 90 else "green"
        ))
    
    def run(self, refresh_interval: float = 2.0):
        """Run the live dashboard"""
        layout = self.create_dashboard()
        
        with Live(layout, refresh_per_second=1, screen=True) as live:
            while True:
                try:
                    self.update_dashboard(layout)
                    time.sleep(refresh_interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.console.print(f"[red]Error: {e}[/red]")
                    time.sleep(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SIDEKICK Network Monitor")
    parser.add_argument("--refresh", type=float, default=2.0, help="Refresh interval in seconds")
    parser.add_argument("--db", type=str, help="Database path")
    
    args = parser.parse_args()
    
    monitor = SidekickMonitor(args.db) if args.db else SidekickMonitor()
    
    try:
        monitor.run(args.refresh)
    except KeyboardInterrupt:
        monitor.console.print("\n[yellow]Monitor stopped by user[/yellow]")
    except Exception as e:
        monitor.console.print(f"[red]Fatal error: {e}[/red]")

if __name__ == "__main__":
    main()