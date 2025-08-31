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
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import workflow orchestration
from workflows import WorkflowOrchestrator

# Load environment variables
load_dotenv()

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
    is_cloud: bool = False
    api_key: Optional[str] = None

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
            ),
            "gpt-oss:120b": ModelCapability(
                name="gpt-oss:120b",
                size_gb=120.0,
                capabilities=["reasoning", "function_calling", "vision", "code", "analysis"],
                performance_tier="cloud",
                preferred_tasks=["complex_reasoning", "multi_modal", "advanced_analysis", "long_context"]
            )
        }
    
    async def discover_instances(self) -> List[OllamaInstance]:
        """Discover available Ollama instances on the network and cloud"""
        discovered = []
        
        # Check Ollama Cloud if configured
        cloud_host = os.getenv("OLLAMA_CLOUD_HOST")
        cloud_api_key = os.getenv("OLLAMA_CLOUD_API_KEY")
        cloud_model = os.getenv("OLLAMA_CLOUD_MODEL", "gpt-oss:120b")
        
        if cloud_host and cloud_api_key:
            cloud_instance = OllamaInstance(
                host=cloud_host.replace("https://", "").replace("http://", ""),
                port=int(os.getenv("OLLAMA_CLOUD_PORT", "443")),
                name="ollama-cloud",
                models=[cloud_model],
                is_available=True,
                last_check=datetime.now(),
                gpu_count=100,
                is_remote=True,
                is_cloud=True,
                api_key=cloud_api_key
            )
            discovered.append(cloud_instance)
        
        # Check Mars instance (localhost)
        mars_host = os.getenv("MARS_HOST", "localhost")
        mars_port = int(os.getenv("MARS_PORT", "11434"))
        instance = await self._check_instance(mars_host, mars_port, "mars-0")
        if instance:
            discovered.append(instance)
        
        # Check Galaxy instances (4 ports)
        galaxy_host = os.getenv("GALAXY_HOST", "192.168.0.162")
        if galaxy_host:
            for i in range(4):
                port = int(os.getenv(f"GALAXY_PORT_{i}", str(11434 + i)))
                instance = await self._check_instance(galaxy_host, port, f"galaxy-{i}")
                if instance:
                    instance.is_remote = True
                    discovered.append(instance)
        
        # Check Explora instances (4 ports)
        explora_host = os.getenv("EXPLORA_HOST", "192.168.0.224")
        if explora_host:
            for i in range(4):
                port = 11434 + i
                instance = await self._check_instance(explora_host, port, f"explora-{i}")
                if instance:
                    instance.is_remote = True
                    discovered.append(instance)
        
        # Check Lunar instance
        lunar_host = os.getenv("LUNAR_HOST", "192.168.0.123")
        lunar_port = int(os.getenv("LUNAR_PORT", "11434"))
        if lunar_host:
            instance = await self._check_instance(lunar_host, lunar_port, "lunar-0")
            if instance:
                instance.is_remote = True
                discovered.append(instance)
        
        # Check Scout instance
        scout_host = os.getenv("SCOUT_HOST", "192.168.0.181")
        scout_port = int(os.getenv("SCOUT_PORT", "11434"))
        if scout_host:
            instance = await self._check_instance(scout_host, scout_port, "scout-0")
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
                    
                    # Get currently loaded models for GPU-aware routing
                    loaded_models = await self._get_loaded_models(host, port)
                    
                    return OllamaInstance(
                        host=host,
                        port=port,
                        name=name,
                        models=models,
                        is_available=True,
                        last_check=datetime.now(),
                        gpu_count=self._estimate_gpu_count(name),
                        loaded_models=loaded_models
                    )
        except Exception as e:
            logger.debug(f"Instance {host}:{port} not available: {e}")
        return None
    
    async def _get_loaded_models(self, host: str, port: int) -> List[Dict[str, Any]]:
        """Get currently loaded models with GPU usage info"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                ps_response = await client.get(f"http://{host}:{port}/api/ps")
                if ps_response.status_code == 200:
                    ps_data = ps_response.json()
                    return ps_data.get("models", [])
        except Exception as e:
            logger.debug(f"Could not get loaded models from {host}:{port}: {e}")
        return []
    
    def _estimate_gpu_count(self, name: str) -> int:
        """Estimate GPU count based on instance name"""
        if "explora" in name:
            return 4  # Explora has 4 GPUs
        elif "galaxy" in name:
            return 4  # Galaxy has 4 GPUs total
        elif "lunar" in name:
            return 1  # Lunar has 1 GPU
        elif "scout" in name:
            return 0  # Scout has no GPU (CPU only)
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
        prompt_lower = prompt.lower()
        
        # Check if cloud model is available and needed
        cloud_available = any(i.is_cloud for i in self.instances.values())
        
        # Use cloud for ultra-complex tasks
        if cloud_available and (
            prompt_length > 2000 or
            "complex" in prompt_lower or
            "advanced" in prompt_lower or
            "analyze" in prompt_lower and prompt_length > 500
        ):
            return "gpt-oss:120b"  # Cloud model for maximum capability
        
        if prompt_length < 100:
            return "phi4"  # Fast model for simple queries
        elif prompt_length < 500:
            return "llama3.1:8b"  # Balanced model
        else:
            return "gpt-oss:20b"  # Powerful model for complex tasks
    
    def _select_instance(self, model: str, requirements: Dict[str, Any]) -> Optional[OllamaInstance]:
        """Select the best instance for the given model with GPU-aware routing"""
        available_instances = [
            instance for instance in self.instances.values()
            if instance.is_available and model in instance.models
        ]
        
        if not available_instances:
            return None
        
        # Prefer cloud for large models
        if model in ["gpt-oss:120b"]:
            cloud_instances = [i for i in available_instances if i.is_cloud]
            if cloud_instances:
                return cloud_instances[0]
        
        # GPU-aware routing: prefer instances with model already loaded
        loaded_instances = [
            instance for instance in available_instances
            if any(loaded["name"] == model for loaded in getattr(instance, "loaded_models", []))
        ]
        
        if loaded_instances:
            # Among loaded instances, prefer those with more free GPU memory
            return self._select_by_gpu_availability(loaded_instances)
        
        # If model not loaded anywhere, prefer instances with more GPUs for complex models
        if any(size in model for size in ["70b", "32b", "30b"]):
            return max(available_instances, key=lambda x: x.gpu_count)
        
        # For smaller models, prefer instances with least GPU load
        return self._select_by_gpu_availability(available_instances)
    
    def _select_by_gpu_availability(self, instances: List[OllamaInstance]) -> OllamaInstance:
        """Select instance with best GPU availability"""
        def gpu_load_score(instance):
            loaded_models = getattr(instance, "loaded_models", [])
            if not loaded_models:
                return 0  # No load = best score
            
            # Calculate total VRAM usage
            total_vram = sum(model.get("size_vram", 0) for model in loaded_models)
            return total_vram / (instance.gpu_count * 1e9)  # Normalize by GPU count
        
        return min(instances, key=gpu_load_score)

    
    async def _execute_on_instance(self, 
                                   instance: OllamaInstance, 
                                   model: str, 
                                   prompt: str) -> Dict[str, Any]:
        """Execute a prompt on a specific instance"""
        try:
            timeout = float(os.getenv("OLLAMA_EXECUTION_TIMEOUT", "300.0"))
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Build URL and headers based on instance type
                if instance.is_cloud:
                    # Ollama Cloud uses HTTPS and requires API key
                    protocol = "https" if instance.port == 443 else "http"
                    url = f"{protocol}://{instance.host}/api/generate"
                    headers = {
                        "Authorization": f"Bearer {instance.api_key}",
                        "Content-Type": "application/json"
                    }
                else:
                    # Local/remote instances use standard HTTP
                    url = f"http://{instance.host}:{instance.port}/api/generate"
                    headers = {"Content-Type": "application/json"}
                
                response = await client.post(
                    url,
                    headers=headers,
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