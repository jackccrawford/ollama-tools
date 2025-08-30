#!/usr/bin/env python3
"""
Ollama Master MCP Server
A Meta-AI Orchestration layer for intelligent Ollama instance management

This MCP server provides:
- Automatic discovery of Ollama instances
- Intelligent request routing based on capabilities
- Load balancing and failover
- Multi-model workflow orchestration
"""

import asyncio
import json
import logging
import socket
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import workflow orchestration
from workflows import WorkflowOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama-master")

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

@dataclass
class ModelCapability:
    """Model capability metadata"""
    name: str
    size_gb: float
    capabilities: List[str]  # ["function_calling", "vision", "code", "reasoning"]
    performance_tier: str  # "fast", "balanced", "powerful"
    preferred_tasks: List[str]

class OllamaMasterServer:
    """Main orchestration server for Ollama instances"""
    
    def __init__(self):
        self.server = Server("ollama-master")
        self.instances: Dict[str, OllamaInstance] = {}
        self.model_capabilities: Dict[str, ModelCapability] = {}
        self._initialize_model_capabilities()
        self.workflow_orchestrator = WorkflowOrchestrator(self)
        
    def _initialize_model_capabilities(self):
        """Initialize known model capabilities"""
        # This will be expanded with actual model metadata
        self.model_capabilities = {
            "phi4": ModelCapability(
                name="phi4",
                size_gb=2.8,
                capabilities=["general", "fast"],
                performance_tier="fast",
                preferred_tasks=["quick_answers", "simple_queries"]
            ),
            "llama3.1:8b": ModelCapability(
                name="llama3.1:8b",
                size_gb=8.0,
                capabilities=["general", "balanced"],
                performance_tier="balanced",
                preferred_tasks=["general_conversation", "analysis"]
            ),
            "gpt-oss:20b": ModelCapability(
                name="gpt-oss:20b",
                size_gb=20.0,
                capabilities=["reasoning", "function_calling"],
                performance_tier="powerful",
                preferred_tasks=["complex_reasoning", "multi_step_tasks"]
            ),
            "codellama:33b": ModelCapability(
                name="codellama:33b",
                size_gb=33.0,
                capabilities=["code", "analysis"],
                performance_tier="powerful",
                preferred_tasks=["code_generation", "code_analysis"]
            )
        }
    
    async def discover_instances(self) -> List[OllamaInstance]:
        """Discover available Ollama instances on the network"""
        discovered = []
        
        # Check local instances (ports 11434-11437)
        for i in range(4):
            port = 11434 + i
            instance = await self._check_instance("localhost", port, f"mars-{i}")
            if instance:
                discovered.append(instance)
        
        # Check remote instances (Explora at 192.168.0.224)
        remote_host = "192.168.0.224"
        for i in range(4):
            port = 11434 + i
            instance = await self._check_instance(remote_host, port, f"explora-{i}")
            if instance:
                instance.is_remote = True
                discovered.append(instance)
        
        # Extended discovery for ports 11434-11499
        # This could be made configurable
        for port in range(11438, 11500):
            instance = await self._check_instance("localhost", port, f"extra-{port}")
            if instance:
                discovered.append(instance)
        
        return discovered
    
    async def _check_instance(self, host: str, port: int, name: str) -> Optional[OllamaInstance]:
        """Check if an Ollama instance is available at host:port"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                # Check if instance is alive
                response = await client.get(f"http://{host}:{port}/api/version")
                if response.status_code == 200:
                    # Get list of models
                    models_response = await client.get(f"http://{host}:{port}/api/tags")
                    models = []
                    if models_response.status_code == 200:
                        models_data = models_response.json()
                        models = [m["name"] for m in models_data.get("models", [])]
                    
                    return OllamaInstance(
                        host=host,
                        port=port,
                        name=name,
                        models=models,
                        is_available=True,
                        last_check=datetime.now(),
                        gpu_count=self._estimate_gpu_count(name)
                    )
        except Exception as e:
            logger.debug(f"Instance {host}:{port} not available: {e}")
        
        return None
    
    def _estimate_gpu_count(self, name: str) -> int:
        """Estimate GPU count based on instance name"""
        if "explora" in name:
            return 4  # Explora has 4 GPUs
        return 1  # Default to 1 for local instances
    
    async def route_request(self, 
                           prompt: str, 
                           requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Intelligently route a request to the best available instance
        
        Requirements can include:
        - model: specific model name
        - performance: "fast", "balanced", "powerful"
        - max_time: maximum seconds for response
        - capabilities: ["function_calling", "vision", etc]
        """
        requirements = requirements or {}
        
        # Refresh instance list
        self.instances = {i.name: i for i in await self.discover_instances()}
        
        # Determine best model and instance
        selected_model = self._select_model(prompt, requirements)
        selected_instance = self._select_instance(selected_model, requirements)
        
        if not selected_instance:
            return {
                "error": "No available instance found",
                "instances_checked": len(self.instances)
            }
        
        # Execute request
        return await self._execute_on_instance(
            selected_instance, 
            selected_model, 
            prompt
        )
    
    def _select_model(self, prompt: str, requirements: Dict[str, Any]) -> str:
        """Select the best model based on prompt and requirements"""
        if "model" in requirements:
            return requirements["model"]
        
        # Analyze prompt complexity (simplified heuristic)
        prompt_length = len(prompt)
        
        if prompt_length < 100:
            return "phi4"  # Fast model for simple queries
        elif prompt_length < 500:
            return "llama3.1:8b"  # Balanced model
        else:
            return "gpt-oss:20b"  # Powerful model for complex tasks
    
    def _select_instance(self, model: str, requirements: Dict[str, Any]) -> Optional[OllamaInstance]:
        """Select the best instance for running the model"""
        available_instances = [
            i for i in self.instances.values() 
            if i.is_available and model in i.models
        ]
        
        if not available_instances:
            # Model not loaded, find instance with capacity
            available_instances = [
                i for i in self.instances.values() 
                if i.is_available
            ]
        
        if not available_instances:
            return None
        
        # Prefer local for small models, remote for large
        model_cap = self.model_capabilities.get(model)
        if model_cap and model_cap.size_gb > 20:
            # Prefer remote GPU cluster for large models
            remote = [i for i in available_instances if i.is_remote]
            if remote:
                return remote[0]
        
        # Return first available local instance
        local = [i for i in available_instances if not i.is_remote]
        return local[0] if local else available_instances[0]
    
    async def _execute_on_instance(self, 
                                   instance: OllamaInstance, 
                                   model: str, 
                                   prompt: str) -> Dict[str, Any]:
        """Execute a prompt on a specific instance"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"http://{instance.host}:{instance.port}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "response": response.json().get("response"),
                        "model": model,
                        "instance": instance.name,
                        "host": f"{instance.host}:{instance.port}"
                    }
                else:
                    return {
                        "error": f"Request failed: {response.status_code}",
                        "instance": instance.name
                    }
        except Exception as e:
            return {
                "error": str(e),
                "instance": instance.name
            }
    
    def setup_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="discover_instances",
                    description="Discover all available Ollama instances on the network",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="route_request",
                    description="Intelligently route a request to the best Ollama instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt to send"},
                            "model": {"type": "string", "description": "Optional specific model"},
                            "performance": {"type": "string", "enum": ["fast", "balanced", "powerful"]},
                            "max_time": {"type": "number", "description": "Maximum response time in seconds"}
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="list_models",
                    description="List all available models across all instances",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="assess_capability",
                    description="Assess if the infrastructure can handle a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_description": {"type": "string"},
                            "requirements": {"type": "object"}
                        },
                        "required": ["task_description"]
                    }
                ),
                Tool(
                    name="execute_workflow",
                    description="Execute a multi-step workflow with intelligent model orchestration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template": {"type": "string", "description": "Workflow template name"},
                            "input_data": {"type": "string", "description": "Input data for the workflow"},
                            "context": {"type": "object", "description": "Optional context"}
                        },
                        "required": ["template", "input_data"]
                    }
                ),
                Tool(
                    name="auto_orchestrate",
                    description="Automatically detect and execute appropriate workflow based on natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Natural language task description"}
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="list_workflows",
                    description="List available workflow templates",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "discover_instances":
                instances = await self.discover_instances()
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "instances": [
                            {
                                "name": i.name,
                                "host": i.host,
                                "port": i.port,
                                "models": i.models,
                                "is_remote": i.is_remote,
                                "gpu_count": i.gpu_count
                            }
                            for i in instances
                        ],
                        "total": len(instances)
                    }, indent=2)
                )]
            
            elif name == "route_request":
                result = await self.route_request(
                    arguments["prompt"],
                    {k: v for k, v in arguments.items() if k != "prompt"}
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "list_models":
                instances = await self.discover_instances()
                all_models = {}
                for instance in instances:
                    for model in instance.models:
                        if model not in all_models:
                            all_models[model] = []
                        all_models[model].append(instance.name)
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "models": all_models,
                        "total_unique": len(all_models)
                    }, indent=2)
                )]
            
            elif name == "assess_capability":
                # Simplified capability assessment
                task = arguments["task_description"]
                requirements = arguments.get("requirements", {})
                
                assessment = {
                    "can_handle": True,
                    "recommended_approach": "",
                    "estimated_time": 0
                }
                
                if "50-page" in task or "large document" in task:
                    assessment["recommended_approach"] = "Use gpt-oss:20b on remote GPU cluster"
                    assessment["estimated_time"] = 120
                elif "quick" in task or "simple" in task:
                    assessment["recommended_approach"] = "Use phi4 on local instance"
                    assessment["estimated_time"] = 5
                else:
                    assessment["recommended_approach"] = "Use llama3.1:8b for balanced performance"
                    assessment["estimated_time"] = 30
                
                return [TextContent(type="text", text=json.dumps(assessment, indent=2))]
            
            elif name == "execute_workflow":
                result = await self.workflow_orchestrator.execute_workflow(
                    arguments["template"],
                    arguments["input_data"],
                    arguments.get("context")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "auto_orchestrate":
                result = await self.workflow_orchestrator.auto_orchestrate(
                    arguments["prompt"]
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "list_workflows":
                workflows = {
                    name: {
                        "description": template.description,
                        "steps": len(template.steps),
                        "estimated_time": template.estimated_time,
                        "required_capabilities": template.required_capabilities
                    }
                    for name, template in self.workflow_orchestrator.templates.items()
                }
                return [TextContent(type="text", text=json.dumps(workflows, indent=2))]
            
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for the MCP server"""
    server = OllamaMasterServer()
    server.setup_tools()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream
        )

if __name__ == "__main__":
    asyncio.run(main())