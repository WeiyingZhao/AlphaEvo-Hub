"""
FastAPI Server

Provides REST API and WebSocket endpoints for Agent Evolve platform.
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging
import json
import asyncio

from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import CodeEvaluator, QAEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agent Evolve API",
    description="API for self-evolving AI agent platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active evolution runs
evolution_runs: Dict[str, Dict[str, Any]] = {}


# Request/Response Models
class AgentConfigRequest(BaseModel):
    model_name: str = "gpt-3.5-turbo"
    model_provider: str = "openai"
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    task: Optional[str] = None


class EvolutionRequest(BaseModel):
    agent_config: AgentConfigRequest
    strategy: str = "prompt_optimization"
    generations: int = 10
    population_size: int = 5
    tasks: Optional[List[str]] = None
    evaluator_type: str = "code"  # code, qa, custom
    evaluator_config: Optional[Dict[str, Any]] = None


class TaskRequest(BaseModel):
    agent_id: str
    task: str
    max_iterations: int = 10


class EvaluationRequest(BaseModel):
    agent_id: str
    tasks: List[str]
    evaluator_type: str = "qa"


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Agent Evolve API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/agent/create")
async def create_agent(config: AgentConfigRequest):
    """
    Create a new agent.

    Returns:
        agent_id and configuration
    """
    try:
        # Create agent
        agent = AgentCore(
            model=config.model_name,
            task=config.task
        )

        if config.system_prompt:
            agent.update_prompt(config.system_prompt)

        # Generate agent ID
        import uuid
        agent_id = str(uuid.uuid4())

        # Store agent
        # In production, use proper database
        if not hasattr(app.state, 'agents'):
            app.state.agents = {}
        app.state.agents[agent_id] = agent

        logger.info(f"Created agent: {agent_id}")

        return {
            "agent_id": agent_id,
            "config": config.dict(),
            "status": "created"
        }

    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/{agent_id}/run")
async def run_agent_task(agent_id: str, request: TaskRequest):
    """
    Run a task with an agent.

    Returns:
        Task result with solution and reasoning trace
    """
    try:
        # Get agent
        if not hasattr(app.state, 'agents') or agent_id not in app.state.agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = app.state.agents[agent_id]

        # Run task
        result = agent.run(
            task=request.task,
            max_iterations=request.max_iterations
        )

        return {
            "agent_id": agent_id,
            "task": request.task,
            "result": result,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Error running task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evolution/start")
async def start_evolution(request: EvolutionRequest):
    """
    Start an evolution run.

    Returns:
        evolution_id to track progress
    """
    try:
        # Create agent
        agent = AgentCore(
            model=request.agent_config.model_name,
            task=request.agent_config.task
        )

        if request.agent_config.system_prompt:
            agent.update_prompt(request.agent_config.system_prompt)

        # Create evaluator
        if request.evaluator_type == "code":
            evaluator = CodeEvaluator(
                test_cases=request.evaluator_config.get("test_cases", []) if request.evaluator_config else []
            )
        elif request.evaluator_type == "qa":
            evaluator = QAEvaluator(
                qa_pairs=request.evaluator_config.get("qa_pairs", []) if request.evaluator_config else []
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown evaluator type: {request.evaluator_type}")

        # Create optimizer
        optimizer = EvolutionaryOptimizer(
            strategy=request.strategy,
            generations=request.generations
        )

        # Generate evolution ID
        import uuid
        evolution_id = str(uuid.uuid4())

        # Store evolution run
        evolution_runs[evolution_id] = {
            "status": "starting",
            "progress": 0,
            "generation": 0,
            "best_score": 0.0,
            "agent": agent,
            "optimizer": optimizer,
            "evaluator": evaluator,
            "tasks": request.tasks or []
        }

        # Start evolution in background
        asyncio.create_task(run_evolution_async(evolution_id))

        logger.info(f"Started evolution: {evolution_id}")

        return {
            "evolution_id": evolution_id,
            "status": "started",
            "config": {
                "strategy": request.strategy,
                "generations": request.generations,
                "population_size": request.population_size
            }
        }

    except Exception as e:
        logger.error(f"Error starting evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_evolution_async(evolution_id: str):
    """Run evolution asynchronously."""
    try:
        run_data = evolution_runs[evolution_id]
        run_data["status"] = "running"

        agent = run_data["agent"]
        optimizer = run_data["optimizer"]
        evaluator = run_data["evaluator"]
        tasks = run_data["tasks"]

        # Run evolution
        result = optimizer.evolve(agent, evaluator, tasks)

        # Update run data
        run_data["status"] = "completed"
        run_data["result"] = result
        run_data["best_score"] = result.best_score
        run_data["progress"] = 100

        logger.info(f"Evolution {evolution_id} completed with score: {result.best_score:.4f}")

    except Exception as e:
        logger.error(f"Evolution {evolution_id} failed: {e}")
        run_data["status"] = "failed"
        run_data["error"] = str(e)


@app.get("/evolution/{evolution_id}/status")
async def get_evolution_status(evolution_id: str):
    """
    Get status of an evolution run.

    Returns:
        Current status, progress, and best score
    """
    if evolution_id not in evolution_runs:
        raise HTTPException(status_code=404, detail="Evolution run not found")

    run_data = evolution_runs[evolution_id]

    return {
        "evolution_id": evolution_id,
        "status": run_data["status"],
        "progress": run_data.get("progress", 0),
        "generation": run_data.get("generation", 0),
        "best_score": run_data.get("best_score", 0.0)
    }


@app.get("/evolution/{evolution_id}/result")
async def get_evolution_result(evolution_id: str):
    """
    Get result of a completed evolution run.

    Returns:
        Evolution result with best configuration
    """
    if evolution_id not in evolution_runs:
        raise HTTPException(status_code=404, detail="Evolution run not found")

    run_data = evolution_runs[evolution_id]

    if run_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Evolution not yet completed")

    result = run_data["result"]

    return {
        "evolution_id": evolution_id,
        "best_score": result.best_score,
        "best_config": result.best_agent_config,
        "generation_scores": result.generation_scores,
        "total_generations": result.total_generations
    }


@app.websocket("/ws/evolution/{evolution_id}")
async def websocket_evolution(websocket: WebSocket, evolution_id: str):
    """
    WebSocket endpoint for real-time evolution updates.
    """
    await websocket.accept()

    try:
        while True:
            if evolution_id not in evolution_runs:
                await websocket.send_json({
                    "error": "Evolution run not found"
                })
                break

            run_data = evolution_runs[evolution_id]

            # Send current status
            await websocket.send_json({
                "status": run_data["status"],
                "progress": run_data.get("progress", 0),
                "generation": run_data.get("generation", 0),
                "best_score": run_data.get("best_score", 0.0)
            })

            # If completed or failed, close connection
            if run_data["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@app.get("/tools/list")
async def list_tools():
    """List available tools."""
    from agent_evolve.tools import ToolManager

    manager = ToolManager()
    tools = manager.list_tools()

    return {
        "tools": tools,
        "count": len(tools)
    }


@app.get("/strategies/list")
async def list_strategies():
    """List available evolution strategies."""
    strategies = [
        {
            "name": "prompt_optimization",
            "description": "Evolves the agent's system prompt for better performance"
        },
        {
            "name": "memory_evolution",
            "description": "Optimizes memory retention and retrieval strategies"
        },
        {
            "name": "tool_evolution",
            "description": "Creates and refines tools for specific tasks"
        },
        {
            "name": "code_evolution",
            "description": "Evolves code solutions using genetic programming"
        }
    ]

    return {
        "strategies": strategies,
        "count": len(strategies)
    }


# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
