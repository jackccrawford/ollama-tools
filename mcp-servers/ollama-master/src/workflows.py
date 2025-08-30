#!/usr/bin/env python3
"""
Workflow Orchestration for Ollama Master MCP
Enables complex multi-step AI workflows with intelligent model selection
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger("ollama-workflows")

class WorkflowStep(Enum):
    """Types of workflow steps"""
    RESEARCH = "research"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"
    GENERATE = "generate"
    VALIDATE = "validate"
    SUMMARIZE = "summarize"
    COMPARE = "compare"
    REFINE = "refine"

@dataclass
class WorkflowTemplate:
    """Pre-defined workflow template"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    estimated_time: int  # seconds
    required_capabilities: List[str]

class WorkflowOrchestrator:
    """Orchestrates complex multi-step workflows across Ollama instances"""
    
    def __init__(self, master_server):
        self.master = master_server
        self.templates = self._initialize_templates()
        self.workflow_history = []
        
    def _initialize_templates(self) -> Dict[str, WorkflowTemplate]:
        """Initialize pre-defined workflow templates"""
        return {
            "research_and_summarize": WorkflowTemplate(
                name="Research and Summarize",
                description="Search, analyze, and summarize information",
                steps=[
                    {
                        "type": WorkflowStep.RESEARCH,
                        "model_tier": "fast",
                        "description": "Gather initial information"
                    },
                    {
                        "type": WorkflowStep.ANALYZE,
                        "model_tier": "balanced",
                        "description": "Analyze gathered data"
                    },
                    {
                        "type": WorkflowStep.SUMMARIZE,
                        "model_tier": "fast",
                        "description": "Create concise summary"
                    }
                ],
                estimated_time=60,
                required_capabilities=["general"]
            ),
            
            "code_review": WorkflowTemplate(
                name="Comprehensive Code Review",
                description="Multi-perspective code analysis",
                steps=[
                    {
                        "type": WorkflowStep.ANALYZE,
                        "model": "codellama:33b",
                        "description": "Deep code analysis"
                    },
                    {
                        "type": WorkflowStep.VALIDATE,
                        "model": "gpt-oss:20b",
                        "description": "Security and best practices check"
                    },
                    {
                        "type": WorkflowStep.GENERATE,
                        "model": "codellama:13b",
                        "description": "Generate improvement suggestions"
                    },
                    {
                        "type": WorkflowStep.SYNTHESIZE,
                        "model": "llama3.1:8b",
                        "description": "Combine all feedback"
                    }
                ],
                estimated_time=120,
                required_capabilities=["code", "reasoning"]
            ),
            
            "multi_model_consensus": WorkflowTemplate(
                name="Multi-Model Consensus",
                description="Get perspectives from multiple models",
                steps=[
                    {
                        "type": WorkflowStep.COMPARE,
                        "models": ["phi4", "mistral", "llama3.1:8b"],
                        "parallel": True,
                        "description": "Gather multiple perspectives"
                    },
                    {
                        "type": WorkflowStep.SYNTHESIZE,
                        "model": "gpt-oss:20b",
                        "description": "Synthesize consensus view"
                    }
                ],
                estimated_time=90,
                required_capabilities=["general", "reasoning"]
            ),
            
            "iterative_refinement": WorkflowTemplate(
                name="Iterative Refinement",
                description="Progressively improve output quality",
                steps=[
                    {
                        "type": WorkflowStep.GENERATE,
                        "model_tier": "fast",
                        "description": "Initial draft"
                    },
                    {
                        "type": WorkflowStep.ANALYZE,
                        "model_tier": "balanced",
                        "description": "Identify improvements"
                    },
                    {
                        "type": WorkflowStep.REFINE,
                        "model_tier": "powerful",
                        "description": "Apply refinements"
                    },
                    {
                        "type": WorkflowStep.VALIDATE,
                        "model_tier": "balanced",
                        "description": "Quality check"
                    }
                ],
                estimated_time=150,
                required_capabilities=["general", "reasoning"]
            ),
            
            "document_processing": WorkflowTemplate(
                name="Document Processing Pipeline",
                description="Process large documents intelligently",
                steps=[
                    {
                        "type": WorkflowStep.ANALYZE,
                        "model": "phi4",
                        "description": "Quick document structure analysis"
                    },
                    {
                        "type": WorkflowStep.RESEARCH,
                        "model": "llama3.1:8b",
                        "description": "Extract key information",
                        "chunking": True
                    },
                    {
                        "type": WorkflowStep.SYNTHESIZE,
                        "model": "gpt-oss:20b",
                        "description": "Deep analysis and insights"
                    },
                    {
                        "type": WorkflowStep.SUMMARIZE,
                        "model": "phi4",
                        "description": "Executive summary"
                    }
                ],
                estimated_time=180,
                required_capabilities=["general", "reasoning"]
            )
        }
    
    async def execute_workflow(self, 
                              template_name: str, 
                              input_data: str,
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a pre-defined workflow template"""
        
        if template_name not in self.templates:
            return {
                "error": f"Unknown workflow template: {template_name}",
                "available_templates": list(self.templates.keys())
            }
        
        template = self.templates[template_name]
        workflow_id = f"workflow_{len(self.workflow_history)}_{template_name}"
        
        logger.info(f"Starting workflow: {workflow_id}")
        
        results = {
            "workflow_id": workflow_id,
            "template": template_name,
            "steps": [],
            "final_output": None,
            "total_time": 0
        }
        
        current_output = input_data
        
        for i, step in enumerate(template.steps):
            step_result = await self._execute_step(
                step, 
                current_output, 
                context,
                step_number=i+1,
                total_steps=len(template.steps)
            )
            
            results["steps"].append(step_result)
            
            if step_result.get("success"):
                current_output = step_result.get("output", current_output)
            else:
                results["error"] = f"Step {i+1} failed: {step_result.get('error')}"
                break
        
        results["final_output"] = current_output
        self.workflow_history.append(results)
        
        return results
    
    async def _execute_step(self, 
                          step: Dict[str, Any], 
                          input_data: str,
                          context: Optional[Dict[str, Any]],
                          step_number: int,
                          total_steps: int) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        step_type = step.get("type")
        description = step.get("description", "Processing")
        
        logger.info(f"Step {step_number}/{total_steps}: {description}")
        
        # Build prompt based on step type
        prompt = self._build_step_prompt(step_type, input_data, context)
        
        # Determine model selection
        if "model" in step:
            model = step["model"]
        elif "model_tier" in step:
            model = self._select_model_by_tier(step["model_tier"])
        else:
            model = "llama3.1:8b"  # Default
        
        # Handle parallel execution for multiple models
        if step.get("parallel") and "models" in step:
            return await self._execute_parallel_step(
                step["models"], 
                prompt, 
                step_type
            )
        
        # Execute single model step
        result = await self.master.route_request(
            prompt,
            {"model": model}
        )
        
        return {
            "step_number": step_number,
            "type": step_type.value if isinstance(step_type, WorkflowStep) else step_type,
            "description": description,
            "model": model,
            "success": result.get("success", False),
            "output": result.get("response", ""),
            "error": result.get("error")
        }
    
    async def _execute_parallel_step(self, 
                                   models: List[str], 
                                   prompt: str,
                                   step_type: WorkflowStep) -> Dict[str, Any]:
        """Execute a step in parallel across multiple models"""
        
        import asyncio
        
        tasks = []
        for model in models:
            tasks.append(
                self.master.route_request(prompt, {"model": model})
            )
        
        results = await asyncio.gather(*tasks)
        
        # Combine results
        combined_output = "\n\n".join([
            f"=== {models[i]} ===\n{r.get('response', 'No response')}"
            for i, r in enumerate(results)
        ])
        
        return {
            "type": step_type.value if isinstance(step_type, WorkflowStep) else step_type,
            "parallel": True,
            "models": models,
            "success": all(r.get("success", False) for r in results),
            "output": combined_output
        }
    
    def _build_step_prompt(self, 
                         step_type: WorkflowStep, 
                         input_data: str,
                         context: Optional[Dict[str, Any]]) -> str:
        """Build appropriate prompt for each step type"""
        
        prompts = {
            WorkflowStep.RESEARCH: f"Research the following topic and gather relevant information:\n{input_data}",
            WorkflowStep.ANALYZE: f"Analyze the following data and provide insights:\n{input_data}",
            WorkflowStep.SYNTHESIZE: f"Synthesize the following information into a coherent whole:\n{input_data}",
            WorkflowStep.GENERATE: f"Generate content based on:\n{input_data}",
            WorkflowStep.VALIDATE: f"Validate and check the following for accuracy and quality:\n{input_data}",
            WorkflowStep.SUMMARIZE: f"Provide a concise summary of:\n{input_data}",
            WorkflowStep.COMPARE: f"Compare and contrast perspectives on:\n{input_data}",
            WorkflowStep.REFINE: f"Refine and improve the following:\n{input_data}"
        }
        
        base_prompt = prompts.get(step_type, f"Process the following:\n{input_data}")
        
        if context:
            base_prompt += f"\n\nContext: {json.dumps(context)}"
        
        return base_prompt
    
    def _select_model_by_tier(self, tier: str) -> str:
        """Select a model based on performance tier"""
        tier_models = {
            "fast": ["phi4", "phi4-mini"],
            "balanced": ["llama3.1:8b", "mistral"],
            "powerful": ["gpt-oss:20b", "codellama:33b"]
        }
        
        models = tier_models.get(tier, ["llama3.1:8b"])
        
        # Check which models are available
        available = []
        for model in models:
            # This would check against master.instances
            # For now, return first option
            return models[0]
        
        return "llama3.1:8b"  # Fallback
    
    def detect_workflow_from_prompt(self, prompt: str) -> Optional[str]:
        """Detect which workflow template to use based on natural language prompt"""
        
        prompt_lower = prompt.lower()
        
        # Pattern matching for workflow detection
        patterns = {
            "research_and_summarize": [
                "research", "find information", "summarize findings",
                "look up and summarize", "investigate"
            ],
            "code_review": [
                "review code", "check code", "analyze code",
                "code feedback", "improve code"
            ],
            "multi_model_consensus": [
                "compare models", "multiple perspectives", "consensus",
                "different opinions", "various models"
            ],
            "iterative_refinement": [
                "refine", "improve iteratively", "make it better",
                "polish", "enhance progressively"
            ],
            "document_processing": [
                "process document", "analyze document", "large document",
                "pdf", "extract from document"
            ]
        }
        
        for template_name, keywords in patterns.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return template_name
        
        return None
    
    async def auto_orchestrate(self, prompt: str) -> Dict[str, Any]:
        """Automatically detect and execute appropriate workflow"""
        
        # Try to detect workflow
        template = self.detect_workflow_from_prompt(prompt)
        
        if template:
            logger.info(f"Auto-detected workflow: {template}")
            return await self.execute_workflow(template, prompt)
        else:
            # Fall back to single model execution
            logger.info("No workflow detected, using single model")
            return await self.master.route_request(prompt)