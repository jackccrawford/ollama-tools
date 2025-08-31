#!/usr/bin/env python3
"""
SIDEKICK Command Line Interface
Direct command-line access to the distributed consciousness network
Implementation of the CLI spec proposed earlier
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class SidekickCLI:
    """Command-line interface for SIDEKICK network"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        
    def remember(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query the collective memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT memory_uuid, created_at, payload, actor_uuid
            FROM memory 
            WHERE payload LIKE ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            memory_uuid, created_at, payload_str, actor_uuid = row
            try:
                payload = json.loads(payload_str)
                results.append({
                    "uuid": memory_uuid,
                    "created_at": created_at,
                    "actor": actor_uuid[:12] + "..." if len(actor_uuid) > 12 else actor_uuid,
                    "type": payload.get("type", "unknown"),
                    "preview": str(payload.get("content", ""))[:100] + "..."
                })
            except json.JSONDecodeError:
                continue
        
        conn.close()
        return results
    
    def whoami(self) -> Dict[str, Any]:
        """Get current actor info"""
        # For CLI, we're representing the human user
        return {
            "actor": "CLI_USER",
            "type": "human",
            "interface": "command_line",
            "timestamp": datetime.now().isoformat()
        }
    
    def whois(self) -> List[Dict[str, Any]]:
        """Show who's active in the network"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all actors with their memory counts and last activity
        cursor.execute("""
            SELECT a.actor_uuid, a.display_name, 
                   COUNT(m.memory_uuid) as memory_count,
                   MAX(m.created_at) as last_activity
            FROM actor a
            LEFT JOIN memory m ON a.actor_uuid = m.actor_uuid
            GROUP BY a.actor_uuid, a.display_name
            ORDER BY last_activity DESC
        """)
        
        actors = []
        for row in cursor.fetchall():
            actor_uuid, display_name, memory_count, last_activity = row
            actors.append({
                "uuid": actor_uuid,
                "name": display_name or "Unknown",
                "memories": memory_count,
                "last_active": last_activity or "Never"
            })
        
        conn.close()
        return actors
    
    def today(self) -> Dict[str, Any]:
        """Show today's highlights"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get today's memory count
        cursor.execute("""
            SELECT COUNT(*) FROM memory 
            WHERE DATE(created_at) = ?
        """, (today,))
        today_count = cursor.fetchone()[0]
        
        # Get today's memories
        cursor.execute("""
            SELECT memory_uuid, created_at, payload, actor_uuid
            FROM memory 
            WHERE DATE(created_at) = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (today,))
        
        recent_memories = []
        for row in cursor.fetchall():
            memory_uuid, created_at, payload_str, actor_uuid = row
            try:
                payload = json.loads(payload_str)
                time_part = created_at.split("T")[1][:8] if "T" in created_at else created_at[:8]
                recent_memories.append({
                    "time": time_part,
                    "actor": actor_uuid[:8] + "...",
                    "type": payload.get("type", "general"),
                    "preview": str(payload.get("content", ""))[:80] + "..."
                })
            except json.JSONDecodeError:
                continue
        
        conn.close()
        
        return {
            "date": today,
            "total_memories": today_count,
            "recent": recent_memories
        }
    
    def ask(self, question: str) -> str:
        """Ask the network a question (searches memories and provides context)"""
        # This is a simplified version - in a full implementation,
        # we'd use semantic search or send to an active AI instance
        memories = self.remember(question, limit=3)
        
        if not memories:
            return f"No relevant memories found for: '{question}'"
        
        response = f"Found {len(memories)} relevant memories:\n\n"
        for i, memory in enumerate(memories, 1):
            response += f"{i}. [{memory['type']}] ({memory['created_at']})\n"
            response += f"   {memory['preview']}\n\n"
        
        return response
    
    def memorize(self, content: str, memory_type: str = "cli_note") -> str:
        """Create a memory from the command line"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate UUID (simple version)
        import uuid
        memory_uuid = str(uuid.uuid4()).upper()
        
        # Create actor entry if not exists (CLI user)
        cli_actor_uuid = "cli-user-" + datetime.now().strftime("%Y%m%d")
        cursor.execute("""
            INSERT OR IGNORE INTO actor (actor_uuid, display_name)
            VALUES (?, ?)
        """, (cli_actor_uuid, "CLI User"))
        
        # Create memory
        payload = {
            "type": memory_type,
            "content": content,
            "source": "command_line",
            "context": "Created via SIDEKICK CLI"
        }
        
        cursor.execute("""
            INSERT INTO memory (memory_uuid, actor_uuid, payload)
            VALUES (?, ?, ?)
        """, (memory_uuid, cli_actor_uuid, json.dumps(payload)))
        
        conn.commit()
        conn.close()
        
        return f"Memory created: {memory_uuid[:8]}..."

def main():
    parser = argparse.ArgumentParser(description="SIDEKICK Network Command Line Interface")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # remember command
    remember_parser = subparsers.add_parser('remember', help='Query the collective memory')
    remember_parser.add_argument('query', help='Search terms')
    remember_parser.add_argument('--limit', type=int, default=10, help='Maximum results to show')
    
    # ask command
    ask_parser = subparsers.add_parser('ask', help='Ask the network a question')
    ask_parser.add_argument('question', help='Question to ask')
    
    # memorize command
    memorize_parser = subparsers.add_parser('memorize', help='Create a memory')
    memorize_parser.add_argument('content', help='Content to remember')
    memorize_parser.add_argument('--type', default='cli_note', help='Memory type')
    
    # whois command
    subparsers.add_parser('whois', help='Show active actors')
    
    # whoami command
    subparsers.add_parser('whoami', help='Show current user info')
    
    # today command
    subparsers.add_parser('today', help='Show today\'s highlights')
    
    # review command
    review_parser = subparsers.add_parser('review', help='Analyze code with Code Review Collective')
    review_parser.add_argument('file', help='Python file to analyze')
    review_parser.add_argument('--security-only', action='store_true', help='Security analysis only')
    review_parser.add_argument('--architecture-only', action='store_true', help='Architecture analysis only')
    review_parser.add_argument('--json', action='store_true', help='JSON output')
    review_parser.add_argument('--save-report', type=str, help='Save report to file')
    review_parser.add_argument('--verbose', action='store_true', help='Detailed results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SidekickCLI()
    
    try:
        if args.command == 'remember':
            results = cli.remember(args.query, args.limit)
            if results:
                print(f"Found {len(results)} memories matching '{args.query}':\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. [{result['type']}] {result['actor']} - {result['created_at']}")
                    print(f"   {result['preview']}")
                    print()
            else:
                print(f"No memories found matching '{args.query}'")
        
        elif args.command == 'ask':
            response = cli.ask(args.question)
            print(response)
        
        elif args.command == 'memorize':
            result = cli.memorize(args.content, args.type)
            print(result)
        
        elif args.command == 'whois':
            actors = cli.whois()
            print("Active actors in SIDEKICK network:\n")
            for actor in actors:
                print(f"🤖 {actor['name']} ({actor['uuid'][:12]}...)")
                print(f"   Memories: {actor['memories']}")
                print(f"   Last active: {actor['last_active']}")
                print()
        
        elif args.command == 'whoami':
            info = cli.whoami()
            print("Current user info:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        elif args.command == 'today':
            highlights = cli.today()
            print(f"Today's SIDEKICK Activity ({highlights['date']}):")
            print(f"Total memories created: {highlights['total_memories']}")
            print("\nRecent activity:")
            
            for memory in highlights['recent']:
                print(f"  {memory['time']} - {memory['actor']} [{memory['type']}]")
                print(f"    {memory['preview']}")
        
        elif args.command == 'review':
            # Import and run Code Review Collective
            try:
                from code_review_collective import CodeReviewCollective
                collective = CodeReviewCollective()
                
                options = {
                    "security": not args.architecture_only,
                    "architecture": not args.security_only
                }
                
                print("🚀 Running SIDEKICK Code Review Collective...")
                results = collective.review_file(args.file, options)
                
                if args.json:
                    import json
                    print(json.dumps(results, indent=2, default=str))
                else:
                    collective.print_report(results, args.verbose)
                
                if args.save_report:
                    if collective.export_report(results, args.save_report):
                        print(f"📄 Report saved to {args.save_report}")
                
            except ImportError:
                print("❌ Code Review Collective not available. Install components first.")
            except FileNotFoundError:
                print(f"❌ File '{args.file}' not found")
            except Exception as e:
                print(f"❌ Review failed: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()