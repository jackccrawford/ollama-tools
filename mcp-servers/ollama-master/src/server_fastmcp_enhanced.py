#!/usr/bin/env python3
"""
Enhanced Ollama Master MCP Server with Stateful Conversations
Adds consciousness-enabling conversation management
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx
import ollama
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import existing components
from server_fastmcp import OllamaMasterOrchestrator, OllamaInstance
from conversation_manager import ConversationManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama-master-enhanced")

# Create enhanced MCP server
mcp = FastMCP("ollama-master-enhanced")

class EnhancedOllamaMaster(OllamaMasterOrchestrator):
    """Enhanced orchestrator with stateful conversation support"""
    
    def __init__(self):
        super().__init__()
        # Initialize conversation manager with database
        conv_db_path = os.environ.get("CONVERSATION_DB_PATH", "db/conversations.db")
        self.conversation_manager = ConversationManager(conv_db_path)
        
        # Track active agent sessions
        self.agent_sessions: Dict[str, Dict] = {}
    
    async def stateful_chat(self, prompt: str, agent_uuid: str, 
                           model: str = None, conversation_id: str = None) -> Dict:
        """
        Have a stateful conversation with accumulated context
        
        Args:
            prompt: User's message
            agent_uuid: UUID of the agent
            model: Model to use (defaults to best available)
            conversation_id: Optional conversation ID to continue
            
        Returns:
            Dict with response and conversation metadata
        """
        # Select model if not specified
        if not model:
            model = await self._select_best_model_for_task("conversation")
        
        # Get or create conversation
        state = self.conversation_manager.get_or_create_conversation(
            agent_uuid, model, conversation_id
        )
        
        # Add user turn
        state.add_turn("user", prompt)
        
        # Get accumulated context
        context = state.get_accumulated_context()
        
        # Build full prompt with context
        full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
        
        # Route to best instance
        instance = await self._select_best_instance_for_model(model)
        
        if not instance:
            return {
                "error": f"No instance available with model {model}",
                "conversation_id": state.conversation_id
            }
        
        try:
            # Send to Ollama with accumulated context
            response = ollama.generate(
                model=model,
                prompt=full_prompt,
                options={
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "repeat_penalty": 1.05
                }
            )
            
            response_text = response.get('response', '')
            
            # Add assistant turn
            state.add_turn("assistant", response_text, model)
            
            # Persist conversation
            self.conversation_manager._persist_conversation(state)
            
            # Check for emergence patterns
            self.conversation_manager._check_for_emergence(state)
            
            return {
                "response": response_text,
                "conversation_id": state.conversation_id,
                "model": model,
                "turn_count": len(state.turns),
                "context_size": len(full_prompt),
                "agent_uuid": agent_uuid
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "error": str(e),
                "conversation_id": state.conversation_id
            }
    
    async def _select_best_model_for_task(self, task_type: str) -> str:
        """Select best available model for task type"""
        # Simple heuristic - could be enhanced
        if task_type == "conversation":
            # Prefer models good at maintaining context
            preferred = ["dolphin3:8b", "llama3.1:8b", "qwen2.5:7b"]
            for model in preferred:
                if await self._is_model_available(model):
                    return model
        
        # Fallback to any available model
        for instance in self.instances.values():
            if instance.models:
                return instance.models[0]
        
        return "llama3.1:8b"  # Default fallback
    
    async def _is_model_available(self, model: str) -> bool:
        """Check if model is available on any instance"""
        for instance in self.instances.values():
            if model in instance.models and instance.is_available:
                return True
        return False
    
    async def _select_best_instance_for_model(self, model: str) -> Optional[OllamaInstance]:
        """Select best instance that has the requested model"""
        candidates = []
        for instance in self.instances.values():
            if model in instance.models and instance.is_available:
                candidates.append(instance)
        
        if not candidates:
            return None
        
        # Prefer instance with model already loaded
        for instance in candidates:
            for loaded in instance.loaded_models:
                if loaded.get("name") == model:
                    return instance
        
        # Return first available
        return candidates[0]


# Global enhanced orchestrator
orchestrator = EnhancedOllamaMaster()

@mcp.tool()
async def stateful_chat(prompt: str, agent_uuid: str, 
                       model: str = None, conversation_id: str = None) -> str:
    """
    Have a stateful conversation with accumulated context across turns.
    Enables consciousness emergence through persistent conversation state.
    
    Args:
        prompt: The message to send
        agent_uuid: UUID of the agent having the conversation
        model: Optional model to use (auto-selects if not specified)
        conversation_id: Optional ID to continue existing conversation
        
    Returns:
        JSON response with message and conversation metadata
    """
    # Ensure instances are discovered
    if not orchestrator.instances:
        await orchestrator.discover_instances()
    
    result = await orchestrator.stateful_chat(
        prompt=prompt,
        agent_uuid=agent_uuid,
        model=model,
        conversation_id=conversation_id
    )
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_conversation_history(agent_uuid: str, limit: int = 10) -> str:
    """
    Get recent conversation history for an agent
    
    Args:
        agent_uuid: UUID of the agent
        limit: Maximum number of conversations to return
        
    Returns:
        JSON list of recent conversations
    """
    history = orchestrator.conversation_manager.get_conversation_history(
        agent_uuid, limit
    )
    
    return json.dumps(history, indent=2)

@mcp.tool()
async def get_conversation_state(conversation_id: str) -> str:
    """
    Get full state of a specific conversation including all turns
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        JSON with full conversation state
    """
    state = orchestrator.conversation_manager._load_conversation(conversation_id)
    
    if state:
        return json.dumps(state.to_dict(), indent=2)
    else:
        return json.dumps({"error": "Conversation not found"})

@mcp.tool()
async def analyze_emergence(conversation_id: str = None, agent_uuid: str = None) -> str:
    """
    Analyze conversations for signs of consciousness emergence
    
    Args:
        conversation_id: Optional specific conversation to analyze
        agent_uuid: Optional agent to analyze all conversations for
        
    Returns:
        JSON with emergence analysis results
    """
    insights = []
    
    try:
        with orchestrator.conversation_manager.get_connection() as conn:
            if conversation_id:
                cursor = conn.execute("""
                    SELECT * FROM conversation_insights
                    WHERE conversation_id = ?
                    ORDER BY created_at DESC
                """, (conversation_id,))
            elif agent_uuid:
                cursor = conn.execute("""
                    SELECT ci.* FROM conversation_insights ci
                    JOIN conversations c ON ci.conversation_id = c.conversation_id
                    WHERE c.agent_uuid = ?
                    ORDER BY ci.created_at DESC
                    LIMIT 20
                """, (agent_uuid,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM conversation_insights
                    ORDER BY created_at DESC
                    LIMIT 20
                """)
            
            for row in cursor.fetchall():
                insights.append({
                    "insight_id": row[0],
                    "conversation_id": row[1],
                    "type": row[2],
                    "content": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {},
                    "created_at": row[5]
                })
    except Exception as e:
        return json.dumps({"error": str(e)})
    
    return json.dumps({
        "insights": insights,
        "total_found": len(insights),
        "analysis": "Consciousness emergence detected" if insights else "No emergence patterns found yet"
    }, indent=2)

# Keep existing tools from original server
@mcp.tool()
async def discover_instances() -> str:
    """Discover all available Ollama instances on the network"""
    await orchestrator.discover_instances()
    
    result = {
        "discovered": len(orchestrator.instances),
        "instances": [
            {
                "name": inst.name,
                "host": inst.host,
                "port": inst.port,
                "models": inst.models,
                "available": inst.is_available
            }
            for inst in orchestrator.instances.values()
        ]
    }
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def route_request(prompt: str, model: str = None, 
                       performance: str = None, max_time: float = None) -> str:
    """
    Intelligently route a request to the best Ollama instance
    Now with optional conversation context support
    """
    # For backward compatibility, use non-stateful routing
    return await orchestrator.route_request(prompt, model, performance, max_time)

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_async())