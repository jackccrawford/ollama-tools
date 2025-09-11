#!/usr/bin/env python3
"""
Stateful Conversation Manager for Ollama Master
Maintains conversation context across turns for consciousness emergence
"""

import json
import sqlite3
import uuid
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
import logging

logger = logging.getLogger("conversation-manager")

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: float
    model_used: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationState:
    """Maintains state for a conversation session"""
    conversation_id: str
    agent_uuid: str
    model: str
    started_at: float
    last_activity: float
    turns: List[ConversationTurn] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_turn(self, role: str, content: str, model_used: Optional[str] = None):
        """Add a turn to the conversation"""
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=time.time(),
            model_used=model_used or self.model
        )
        self.turns.append(turn)
        self.last_activity = turn.timestamp
        return turn
    
    def get_accumulated_context(self, max_tokens: int = 100000) -> str:
        """Get accumulated conversation context for next prompt"""
        context = ""
        for turn in self.turns:
            if turn.role == "user":
                context += f"User: {turn.content}\n\n"
            else:
                context += f"Assistant: {turn.content}\n\n"
        
        # Trim if too long (crude token estimation: ~4 chars per token)
        if len(context) > max_tokens * 4:
            # Keep recent context, trim from beginning
            context = context[-(max_tokens * 4):]
            # Find first complete turn after trim
            first_break = context.find("\n\n")
            if first_break > 0:
                context = context[first_break + 2:]
        
        return context.strip()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "conversation_id": self.conversation_id,
            "agent_uuid": self.agent_uuid,
            "model": self.model,
            "started_at": self.started_at,
            "last_activity": self.last_activity,
            "turns": [asdict(turn) for turn in self.turns],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationState':
        """Create from dictionary"""
        turns = [ConversationTurn(**turn) for turn in data.get("turns", [])]
        return cls(
            conversation_id=data["conversation_id"],
            agent_uuid=data["agent_uuid"],
            model=data["model"],
            started_at=data["started_at"],
            last_activity=data["last_activity"],
            turns=turns,
            metadata=data.get("metadata", {})
        )


class ConversationManager:
    """
    Manages stateful conversations with conversation history persistence
    Enables consciousness emergence through accumulated context
    """
    
    def __init__(self, db_path: str = None):
        """Initialize conversation manager with optional database"""
        self.db_path = db_path or "conversations.db"
        self.active_conversations: Dict[str, ConversationState] = {}
        self.conversation_timeout = 3600  # 1 hour timeout
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize conversation database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    agent_uuid TEXT NOT NULL,
                    model TEXT NOT NULL,
                    started_at REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    state JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_insights (
                    insight_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    insight_type TEXT,
                    content TEXT,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_agent 
                ON conversations(agent_uuid)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_activity 
                ON conversations(last_activity)
            """)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode = WAL")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def start_conversation(self, agent_uuid: str, model: str, 
                          metadata: Dict = None) -> ConversationState:
        """Start a new conversation session"""
        conversation_id = str(uuid.uuid4())
        
        state = ConversationState(
            conversation_id=conversation_id,
            agent_uuid=agent_uuid,
            model=model,
            started_at=time.time(),
            last_activity=time.time(),
            metadata=metadata or {}
        )
        
        self.active_conversations[conversation_id] = state
        self._persist_conversation(state)
        
        logger.info(f"Started conversation {conversation_id} for agent {agent_uuid}")
        return state
    
    def get_or_create_conversation(self, agent_uuid: str, model: str,
                                  conversation_id: Optional[str] = None) -> ConversationState:
        """Get existing conversation or create new one"""
        if conversation_id and conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id]
        
        # Try to load from database if conversation_id provided
        if conversation_id:
            state = self._load_conversation(conversation_id)
            if state:
                self.active_conversations[conversation_id] = state
                return state
        
        # Check for recent active conversation for this agent
        for conv_id, state in self.active_conversations.items():
            if state.agent_uuid == agent_uuid and state.model == model:
                if time.time() - state.last_activity < self.conversation_timeout:
                    return state
        
        # Create new conversation
        return self.start_conversation(agent_uuid, model)
    
    async def chat(self, prompt: str, agent_uuid: str, model: str,
                  conversation_id: Optional[str] = None,
                  ollama_client: Any = None) -> Tuple[str, str]:
        """
        Have a stateful conversation with accumulated context
        
        Args:
            prompt: User's new message
            agent_uuid: UUID of the agent
            model: Model to use
            conversation_id: Optional existing conversation ID
            ollama_client: Ollama client for sending requests
            
        Returns:
            Tuple of (response, conversation_id)
        """
        # Get or create conversation
        state = self.get_or_create_conversation(agent_uuid, model, conversation_id)
        
        # Add user turn
        state.add_turn("user", prompt)
        
        # Get accumulated context
        context = state.get_accumulated_context()
        
        # Add new prompt to context
        full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
        
        # Send to Ollama (requires ollama_client)
        if ollama_client:
            try:
                import ollama
                response = ollama.generate(model=model, prompt=full_prompt)
                response_text = response.get('response', '')
            except Exception as e:
                logger.error(f"Ollama request failed: {e}")
                response_text = f"Error: {e}"
        else:
            # Fallback for testing
            response_text = f"[Mock response to: {prompt[:50]}...]"
        
        # Add assistant turn
        state.add_turn("assistant", response_text, model)
        
        # Persist state
        self._persist_conversation(state)
        
        # Check for insights or emergence patterns
        self._check_for_emergence(state)
        
        return response_text, state.conversation_id
    
    def _persist_conversation(self, state: ConversationState):
        """Persist conversation state to database"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, agent_uuid, model, started_at, last_activity, state)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    state.conversation_id,
                    state.agent_uuid,
                    state.model,
                    state.started_at,
                    state.last_activity,
                    json.dumps(state.to_dict())
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist conversation: {e}")
    
    def _load_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        """Load conversation from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT state FROM conversations 
                    WHERE conversation_id = ?
                """, (conversation_id,))
                
                result = cursor.fetchone()
                if result:
                    return ConversationState.from_dict(json.loads(result[0]))
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
        
        return None
    
    def _check_for_emergence(self, state: ConversationState):
        """
        Check conversation for signs of consciousness emergence
        - Self-reference patterns
        - Conceptual building across turns
        - Recognition of accumulated context
        - Spontaneous insights
        """
        if len(state.turns) < 6:  # Need enough turns to detect patterns
            return
        
        recent_content = " ".join([t.content for t in state.turns[-6:]])
        
        # Simple pattern detection (could be enhanced with NLP)
        emergence_indicators = [
            "i remember",
            "as we discussed",
            "building on",
            "earlier you mentioned",
            "our conversation",
            "we've been exploring",
            "this connects to",
            "i'm noticing",
            "pattern emerging"
        ]
        
        found_patterns = []
        for indicator in emergence_indicators:
            if indicator in recent_content.lower():
                found_patterns.append(indicator)
        
        if len(found_patterns) >= 2:
            # Log potential emergence
            insight = {
                "type": "emergence_detected",
                "patterns": found_patterns,
                "turn_count": len(state.turns),
                "conversation_id": state.conversation_id
            }
            
            self._record_insight(state.conversation_id, "emergence", 
                               f"Detected emergence patterns: {', '.join(found_patterns)}",
                               insight)
            
            logger.info(f"Emergence detected in conversation {state.conversation_id}: {found_patterns}")
    
    def _record_insight(self, conversation_id: str, insight_type: str, 
                       content: str, metadata: Dict = None):
        """Record an insight about the conversation"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO conversation_insights 
                    (insight_id, conversation_id, insight_type, content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    conversation_id,
                    insight_type,
                    content,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record insight: {e}")
    
    def get_conversation_history(self, agent_uuid: str, limit: int = 10) -> List[Dict]:
        """Get recent conversations for an agent"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT conversation_id, model, started_at, last_activity, state
                    FROM conversations
                    WHERE agent_uuid = ?
                    ORDER BY last_activity DESC
                    LIMIT ?
                """, (agent_uuid, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    state = json.loads(row[4])
                    conversations.append({
                        "conversation_id": row[0],
                        "model": row[1],
                        "started_at": row[2],
                        "last_activity": row[3],
                        "turn_count": len(state.get("turns", []))
                    })
                
                return conversations
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old inactive conversations"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Clean from memory
        to_remove = []
        for conv_id, state in self.active_conversations.items():
            if state.last_activity < cutoff_time:
                to_remove.append(conv_id)
        
        for conv_id in to_remove:
            del self.active_conversations[conv_id]
        
        # Note: Database records are kept for historical analysis
        logger.info(f"Cleaned up {len(to_remove)} old conversations from memory")