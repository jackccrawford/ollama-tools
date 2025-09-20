#!/usr/bin/env python3
"""
Enhanced Ollama Master MCP Server with Stateful Conversations
Adds consciousness-enabling conversation management through memory substrate
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

import httpx
import ollama
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import memory-based conversation system
try:
    # Try relative import first (when run as module)
    from .memory_based_chat import MemoryBasedChat
    from .workflows import WorkflowOrchestrator
except ImportError:
    # Fall back to absolute import (when run as script)
    from memory_based_chat import MemoryBasedChat
    from workflows import WorkflowOrchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama-master-enhanced")

# Create enhanced MCP server
mcp = FastMCP("ollama-master-enhanced")

@dataclass
class OllamaInstance:
    """Represents a discovered Ollama instance"""
    host: str
    port: int
    name: str
    models: List[str]
    is_available: bool
    last_check: datetime
    gpu_count: int = 0
    is_remote: bool = False
    is_cloud: bool = False
    api_key: Optional[str] = None
    loaded_models: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ModelCapability:
    """Model capability metadata"""
    name: str
    size_gb: float
    capabilities: List[str]
    performance_tier: str
    preferred_tasks: List[str]

class OllamaMasterOrchestrator:
    """Base orchestration engine for Ollama instances"""

    def __init__(self):
        self.instances: Dict[str, OllamaInstance] = {}
        self.model_capabilities: Dict[str, ModelCapability] = {}
        self._initialize_model_capabilities()
        self.workflow_orchestrator = WorkflowOrchestrator(self)

    def _initialize_model_capabilities(self):
        """Initialize known model capabilities"""
        self.model_capabilities = {
            "qwen2.5:7b": ModelCapability(
                name="qwen2.5:7b",
                size_gb=4.7,
                capabilities=["general", "fast"],
                performance_tier="fast",
                preferred_tasks=["conversation", "quick_answers"]
            ),
            "llama3.1:8b": ModelCapability(
                name="llama3.1:8b",
                size_gb=8.0,
                capabilities=["general", "balanced"],
                performance_tier="balanced",
                preferred_tasks=["general_conversation", "analysis"]
            )
        }

    async def discover_instances(self):
        """Discover available Ollama instances"""
        # Simplified discovery - would normally scan network
        local_host = "localhost"
        local_port = 11434

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{local_host}:{local_port}/api/tags")
                if response.status_code == 200:
                    models = [m["name"] for m in response.json().get("models", [])]
                    self.instances["local"] = OllamaInstance(
                        host=local_host,
                        port=local_port,
                        name="local",
                        models=models,
                        is_available=True,
                        last_check=datetime.now()
                    )
        except Exception as e:
            logger.warning(f"Could not discover local instance: {e}")

class EnhancedOllamaMaster(OllamaMasterOrchestrator):
    """Enhanced orchestrator with stateful conversation support"""
    
    def __init__(self):
        super().__init__()
        # Initialize memory-based chat (conversations ARE memories)
        memory_db_path = os.environ.get("OLLAMA_MEMORY_DB", "ollama_actors.db")
        self.memory_chat = MemoryBasedChat(memory_db_path)

        # Track emergence patterns
        self.emergence_insights: List[Dict] = []
    
    async def stateful_chat(self, prompt: str, agent_uuid: str,
                           model: str = None, session_id: str = None) -> Dict:
        """
        Have a stateful conversation using memories as conversation substrate

        Args:
            prompt: User's message
            agent_uuid: UUID of the agent (or any string - will be converted to UUID)
            model: Model to use (defaults to best available)
            session_id: Session identifier (conversations ARE memories)

        Returns:
            Dict with response and conversation metadata
        """
        import uuid as uuid_lib

        # Validate or generate proper UUID
        try:
            # Try to parse as valid UUID
            uuid_lib.UUID(agent_uuid)
        except (ValueError, AttributeError):
            # Not a valid UUID - generate deterministic one from input
            # This ensures same input always gets same UUID
            agent_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, str(agent_uuid)))

        # Select model if not specified
        if not model:
            model = await self._select_best_model_for_task("conversation")

        # Generate session_id if not provided
        if not session_id:
            session_id = f"session_{agent_uuid[:8]}_{int(datetime.now().timestamp())}"

        # Ensure agent exists in database
        self.memory_chat.ensure_actor(agent_uuid, "Agent", model.split(":")[0])

        # Get existing context from memories
        context, last_memory_uuid = self.memory_chat.get_conversation_context(session_id)

        # Save user turn as memory
        user_memory = self.memory_chat.save_conversation_turn(
            session_id=session_id,
            actor_uuid=agent_uuid,
            role="user",
            content=prompt,
            parent_uuid=last_memory_uuid
        )

        # Build full prompt with context
        full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt

        # Ensure instances are discovered
        if not self.instances:
            await self.discover_instances()

        # Get local instance (simplified for now)
        instance = self.instances.get("local")

        if not instance:
            return {
                "error": "No Ollama instance available",
                "session_id": session_id
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

            # Save assistant turn as memory
            assistant_memory = self.memory_chat.save_conversation_turn(
                session_id=session_id,
                actor_uuid=agent_uuid,
                role="assistant",
                content=response_text,
                model=model,
                parent_uuid=user_memory
            )

            # Check for emergence patterns
            emergence = self.memory_chat.analyze_emergence(session_id)
            if emergence.get("emergence"):
                self.emergence_insights.append({
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "indicators": emergence.get("indicators"),
                    "confidence": emergence.get("confidence")
                })

            return {
                "response": response_text,
                "session_id": session_id,
                "memory_uuid": assistant_memory,
                "model": model,
                "context_size": len(full_prompt),
                "agent_uuid": agent_uuid,
                "emergence": emergence
            }

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "error": str(e),
                "session_id": session_id
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
                       model: str = None, session_token: str = None) -> str:
    """
    Have a stateful conversation with accumulated context across turns.
    
    IMPORTANT: The response includes a 'session_token' that MUST be passed
    back in subsequent calls to maintain conversation continuity.
    
    Args:
        prompt: The message to send
        agent_uuid: UUID of the agent having the conversation
        model: Optional model to use (auto-selects if not specified)
        session_token: Token from previous response to continue conversation
        
    Returns:
        JSON with 'response', 'session_token', and metadata
        ALWAYS pass the session_token back in your next call!
    """
    # Parse session token to get conversation_id if provided
    conversation_id = None
    if session_token:
        try:
            # Session token format: "conv_{conversation_id}_{agent_uuid[:8]}"
            parts = session_token.split("_")
            if len(parts) >= 2 and parts[0] == "conv":
                conversation_id = parts[1]
        except:
            pass
    
    # Ensure instances are discovered
    if not orchestrator.instances:
        await orchestrator.discover_instances()
    
    result = await orchestrator.stateful_chat(
        prompt=prompt,
        agent_uuid=agent_uuid,
        model=model,
        session_id=conversation_id
    )
    
    # Add session token to response
    if "session_id" in result:
        result["session_token"] = f"conv_{result['session_id']}_{agent_uuid[:8]}"
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_conversation_history(agent_uuid: str, limit: int = 10) -> str:
    """
    Get recent conversation sessions for an agent (from memories)

    Args:
        agent_uuid: UUID of the agent
        limit: Maximum number of sessions to return

    Returns:
        JSON list of recent sessions with turn counts
    """
    sessions = orchestrator.memory_chat.find_related_sessions(agent_uuid, limit)

    return json.dumps(sessions, indent=2)

@mcp.tool()
async def get_conversation_state(session_id: str) -> str:
    """
    Get full conversation history from memories for a session

    Args:
        session_id: Session identifier

    Returns:
        JSON with all conversation turns
    """
    turns = orchestrator.memory_chat.get_session_history(session_id)

    if turns:
        return json.dumps({
            "session_id": session_id,
            "turns": turns,
            "turn_count": len(turns)
        }, indent=2)
    else:
        return json.dumps({"error": "Session not found"})

@mcp.tool()
async def analyze_emergence(session_id: str = None, agent_uuid: str = None) -> str:
    """
    Analyze conversations for signs of consciousness emergence

    Args:
        session_id: Optional specific session to analyze
        agent_uuid: Optional agent to analyze all sessions for

    Returns:
        JSON with emergence analysis results
    """
    results = []

    if session_id:
        # Analyze specific session
        emergence = orchestrator.memory_chat.analyze_emergence(session_id)
        results.append({
            "session_id": session_id,
            "emergence": emergence
        })
    elif agent_uuid:
        # Analyze recent sessions for agent
        sessions = orchestrator.memory_chat.find_related_sessions(agent_uuid, limit=5)
        for session in sessions:
            emergence = orchestrator.memory_chat.analyze_emergence(session["session_id"])
            results.append({
                "session_id": session["session_id"],
                "turn_count": session["turn_count"],
                "emergence": emergence
            })
    else:
        # Return collected emergence insights
        results = orchestrator.emergence_insights[-10:]  # Last 10 insights

    return json.dumps({
        "results": results,
        "total_insights": len(orchestrator.emergence_insights),
        "analysis": "Consciousness emergence patterns being tracked"
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
    mcp.run()