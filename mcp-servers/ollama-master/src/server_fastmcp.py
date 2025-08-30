#!/usr/bin/env python3
"""
Ollama Master MCP Server (FastMCP Version)
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
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import httpx
from mcp.server.fastmcp import FastMCP

# Import workflow orchestration
from workflows import WorkflowOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama-master")

# Create MCP server
mcp = FastMCP("ollama-master")

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

class OllamaMasterOrchestrator:
    """Main orchestration engine for Ollama instances"""
    
    def __init__(self):
        self.instances: Dict[str, OllamaInstance] = {}
        self.model_capabilities: Dict[str, ModelCapability] = {}
        self._initialize_model_capabilities()
        self.workflow_orchestrator = WorkflowOrchestrator(self)
        
    def _initialize_model_capabilities(self):
        """Initialize known model capabilities"""
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
        
        return discovered
    
    async def _check_instance(self, host: str, port: int, name: str) -> Optional[OllamaInstance]:
        """Check if an Ollama instance is available at host:port"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"http://{host}:{port}/api/version")
                if response.status_code == 200:
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
        """Intelligently route a request to the best available instance"""
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
        
        return await self._execute_on_instance(
            selected_instance, 
            selected_model, 
            prompt
        )
    
    def _select_model(self, prompt: str, requirements: Dict[str, Any]) -> str:
        """Select the best model based on prompt and requirements"""
        if "model" in requirements:
            return requirements["model"]
        
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
            available_instances = [
                i for i in self.instances.values() 
                if i.is_available
            ]
        
        if not available_instances:
            return None
        
        model_cap = self.model_capabilities.get(model)
        if model_cap and model_cap.size_gb > 20:
            remote = [i for i in available_instances if i.is_remote]
            if remote:
                return remote[0]
        
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

# Create global orchestrator instance
orchestrator = OllamaMasterOrchestrator()

@mcp.tool()
async def discover_instances() -> str:
    """Discover all available Ollama instances on the network
    
    Returns:
        JSON string with discovered instances and their details
    """
    instances = await orchestrator.discover_instances()
    return json.dumps({
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

@mcp.tool()
async def route_request(prompt: str, model: str = None, performance: str = None, max_time: float = None) -> str:
    """Intelligently route a request to the best Ollama instance
    
    Args:
        prompt: The prompt to send
        model: Optional specific model to use
        performance: Optional performance tier (fast, balanced, powerful)
        max_time: Optional maximum response time in seconds
    
    Returns:
        JSON string with response and routing details
    """
    requirements = {}
    if model:
        requirements["model"] = model
    if performance:
        requirements["performance"] = performance
    if max_time:
        requirements["max_time"] = max_time
    
    result = await orchestrator.route_request(prompt, requirements)
    return json.dumps(result, indent=2)

@mcp.tool()
async def list_models() -> str:
    """List all available models across all instances
    
    Returns:
        JSON string with models and their availability
    """
    instances = await orchestrator.discover_instances()
    all_models = {}
    for instance in instances:
        for model in instance.models:
            if model not in all_models:
                all_models[model] = []
            all_models[model].append(instance.name)
    
    return json.dumps({
        "models": all_models,
        "total_unique": len(all_models)
    }, indent=2)

@mcp.tool()
async def assess_capability(task_description: str, requirements: dict = None) -> str:
    """Assess if the infrastructure can handle a specific task
    
    Args:
        task_description: Description of the task to assess
        requirements: Optional specific requirements
    
    Returns:
        JSON string with capability assessment
    """
    requirements = requirements or {}
    task = task_description.lower()
    
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
    
    return json.dumps(assessment, indent=2)

@mcp.tool()
async def execute_workflow(template: str, input_data: str, context: dict = None) -> str:
    """Execute a multi-step workflow with intelligent model orchestration
    
    Args:
        template: Workflow template name
        input_data: Input data for the workflow
        context: Optional context for the workflow
    
    Returns:
        JSON string with workflow execution results
    """
    result = await orchestrator.workflow_orchestrator.execute_workflow(
        template, input_data, context
    )
    return json.dumps(result, indent=2)

@mcp.tool()
async def auto_orchestrate(prompt: str) -> str:
    """Automatically detect and execute appropriate workflow based on natural language
    
    Args:
        prompt: Natural language task description
    
    Returns:
        JSON string with orchestration results
    """
    result = await orchestrator.workflow_orchestrator.auto_orchestrate(prompt)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_workflows() -> str:
    """List available workflow templates
    
    Returns:
        JSON string with available workflows
    """
    workflows = {
        name: {
            "description": template.description,
            "steps": len(template.steps),
            "estimated_time": template.estimated_time,
            "required_capabilities": template.required_capabilities
        }
        for name, template in orchestrator.workflow_orchestrator.templates.items()
    }
    return json.dumps(workflows, indent=2)

if __name__ == "__main__":
    mcp.run()