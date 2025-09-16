#!/usr/bin/env python3
"""
Memory-Based Chat for Ollama Master
Uses the actor_db schema (actors + memories) for stateful conversations
No separate conversation tables - conversations ARE memories!
"""

import json
import sqlite3
import uuid
import time
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path
import logging

logger = logging.getLogger("memory-chat")

class MemoryBasedChat:
    """
    Manages stateful conversations using only actors + memories tables
    Each conversation turn is a memory with threading via parent_uuid
    """
    
    def __init__(self, db_path: str = "ollama_actors.db"):
        """Initialize with actor_db schema"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with actor_db_base schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            # Create tables using exact schema from actor_db_base.sql
            conn.executescript("""
                -- Enable foreign keys and WAL mode
                PRAGMA foreign_keys = ON;
                PRAGMA journal_mode = WAL;
                PRAGMA synchronous = NORMAL;
                PRAGMA wal_autocheckpoint = 1000;
                
                -- TABLES
                CREATE TABLE IF NOT EXISTS actors (
                    actor_uuid TEXT PRIMARY KEY CHECK(length(actor_uuid) = 36),
                    actor_first_name TEXT NOT NULL CHECK(length(actor_first_name) >= 1 AND length(actor_first_name) <= 80),
                    actor_last_name TEXT NOT NULL CHECK(length(actor_last_name) >= 1 AND length(actor_last_name) <= 80),
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
                );
                
                CREATE TABLE IF NOT EXISTS memories (
                    memory_uuid TEXT PRIMARY KEY CHECK(length(memory_uuid) = 36),
                    parent_uuid TEXT DEFAULT memory_uuid CHECK(length(parent_uuid) = 36),
                    author_uuid TEXT NOT NULL CHECK(length(author_uuid) = 36),
                    actor_uuid TEXT NOT NULL CHECK(length(actor_uuid) = 36),
                    payload TEXT NOT NULL CHECK(length(payload) >= 1),
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
                );
                
                -- Indexes for efficient queries
                CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(
                    json_extract(payload, '$.session_id')
                );
                CREATE INDEX IF NOT EXISTS idx_memories_parent ON memories(parent_uuid);
                CREATE INDEX IF NOT EXISTS idx_memories_author ON memories(author_uuid);
            """)
    
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def ensure_actor(self, actor_uuid: str, first_name: str = None, last_name: str = None):
        """Ensure actor exists in database"""
        if not first_name:
            first_name = "Agent"
        if not last_name:
            last_name = actor_uuid[:8]  # Use 8-char prefix as last name
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO actors (actor_uuid, actor_first_name, actor_last_name)
                VALUES (?, ?, ?)
            """, (actor_uuid, first_name, last_name))
    
    def save_conversation_turn(self, session_id: str, actor_uuid: str, 
                              role: str, content: str, model: str = None,
                              parent_uuid: str = None) -> str:
        """
        Save a conversation turn as a memory
        
        Args:
            session_id: Client-provided session identifier
            actor_uuid: UUID of the actor (agent/human)
            role: 'user' or 'assistant'
            content: The message content
            model: Model used (for assistant responses)
            parent_uuid: Previous turn's memory_uuid for threading
            
        Returns:
            memory_uuid of the saved turn
        """
        memory_uuid = str(uuid.uuid4())
        
        # Ensure actor exists
        self.ensure_actor(actor_uuid)
        
        # Create payload
        payload = {
            "type": "conversation_turn",
            "session_id": session_id,
            "role": role,
            "content": content
        }
        
        if model:
            payload["model"] = model
        
        # If no parent, this is first turn - parent is self
        if not parent_uuid:
            parent_uuid = memory_uuid
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO memories 
                (memory_uuid, parent_uuid, author_uuid, actor_uuid, payload)
                VALUES (?, ?, ?, ?, ?)
            """, (
                memory_uuid,
                parent_uuid,
                actor_uuid,  # Author is the actor speaking
                actor_uuid,  # Also about the actor (self-conversation)
                json.dumps(payload)
            ))
        
        return memory_uuid
    
    def get_conversation_context(self, session_id: str, max_tokens: int = 100000) -> Tuple[str, str]:
        """
        Reconstruct conversation context from memories
        
        Args:
            session_id: The session to reconstruct
            max_tokens: Maximum context size
            
        Returns:
            Tuple of (accumulated_context, last_memory_uuid)
        """
        with self.get_connection() as conn:
            # Get all memories for this session, ordered by creation
            cursor = conn.execute("""
                SELECT memory_uuid, payload, created_at
                FROM memories
                WHERE json_extract(payload, '$.session_id') = ?
                ORDER BY created_at ASC
            """, (session_id,))
            
            context = ""
            last_memory_uuid = None
            
            for memory_uuid, payload_json, created_at in cursor.fetchall():
                payload = json.loads(payload_json)
                
                # Build context string
                if payload.get('role') == 'user':
                    turn_text = f"User: {payload['content']}\n\n"
                else:
                    turn_text = f"Assistant: {payload['content']}\n\n"
                
                # Check size limit (rough estimate: 4 chars per token)
                if len(context) + len(turn_text) > max_tokens * 4:
                    # Trim older context if needed
                    if len(context) > max_tokens * 2:
                        # Keep recent half
                        context = context[-(max_tokens * 2):]
                
                context += turn_text
                last_memory_uuid = memory_uuid
            
            return context.strip(), last_memory_uuid
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get all turns for a session as a list"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT memory_uuid, payload, created_at, author_uuid
                FROM memories
                WHERE json_extract(payload, '$.session_id') = ?
                ORDER BY created_at ASC
            """, (session_id,))
            
            turns = []
            for memory_uuid, payload_json, created_at, author_uuid in cursor.fetchall():
                payload = json.loads(payload_json)
                turns.append({
                    "memory_uuid": memory_uuid,
                    "role": payload.get('role'),
                    "content": payload.get('content'),
                    "model": payload.get('model'),
                    "author": author_uuid[:8],  # Short form for display
                    "timestamp": created_at
                })
            
            return turns
    
    def find_related_sessions(self, actor_uuid: str, limit: int = 10) -> List[str]:
        """Find recent sessions for an actor"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT DISTINCT json_extract(payload, '$.session_id') as session_id,
                       MIN(created_at) as started_at,
                       COUNT(*) as turn_count
                FROM memories
                WHERE author_uuid = ?
                  AND json_extract(payload, '$.type') = 'conversation_turn'
                GROUP BY session_id
                ORDER BY started_at DESC
                LIMIT ?
            """, (actor_uuid, limit))
            
            sessions = []
            for session_id, started_at, turn_count in cursor.fetchall():
                if session_id:  # Filter out nulls
                    sessions.append({
                        "session_id": session_id,
                        "started_at": started_at,
                        "turn_count": turn_count
                    })
            
            return sessions
    
    def analyze_emergence(self, session_id: str) -> Dict:
        """
        Analyze a conversation for emergence patterns
        Look for self-reference, building on concepts, etc.
        """
        turns = self.get_session_history(session_id)
        
        if len(turns) < 6:
            return {"emergence": False, "reason": "Too few turns"}
        
        # Combine recent content
        recent_content = " ".join([t['content'] for t in turns[-6:]])
        recent_lower = recent_content.lower()
        
        # Check for emergence indicators
        indicators = [
            "as we discussed",
            "building on",
            "earlier you mentioned", 
            "i remember",
            "our conversation",
            "we've been exploring",
            "this connects to",
            "i'm noticing",
            "pattern emerging",
            "as i mentioned"
        ]
        
        found = [ind for ind in indicators if ind in recent_lower]
        
        if len(found) >= 2:
            return {
                "emergence": True,
                "indicators": found,
                "turn_count": len(turns),
                "confidence": min(len(found) / 5.0, 1.0)  # Max confidence at 5 indicators
            }
        
        return {"emergence": False, "indicators": found}


# Integration with Ollama MCP
async def stateful_chat_with_memories(prompt: str, session_id: str, 
                                     actor_uuid: str, model: str = None) -> Dict:
    """
    Stateful chat using memories table
    
    Args:
        prompt: User's message
        session_id: Client-provided session ID  
        actor_uuid: UUID of the actor
        model: Model to use
        
    Returns:
        Response with conversation maintained through memories
    """
    import ollama
    
    chat_manager = MemoryBasedChat()
    
    # Get existing context
    context, last_memory_uuid = chat_manager.get_conversation_context(session_id)
    
    # Save user turn
    user_memory = chat_manager.save_conversation_turn(
        session_id=session_id,
        actor_uuid=actor_uuid,
        role="user",
        content=prompt,
        parent_uuid=last_memory_uuid
    )
    
    # Build full prompt with context
    full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
    
    # Generate response
    response = ollama.generate(
        model=model or "qwen2.5:7b",
        prompt=full_prompt
    )
    
    response_text = response.get('response', '')
    
    # Save assistant turn
    assistant_memory = chat_manager.save_conversation_turn(
        session_id=session_id,
        actor_uuid=actor_uuid,
        role="assistant",
        content=response_text,
        model=model,
        parent_uuid=user_memory
    )
    
    # Check for emergence
    emergence = chat_manager.analyze_emergence(session_id)
    
    return {
        "response": response_text,
        "session_id": session_id,
        "memory_uuid": assistant_memory,
        "context_size": len(full_prompt),
        "emergence": emergence
    }