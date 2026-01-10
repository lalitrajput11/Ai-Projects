"""FastAPI server for autonomous agent."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import time
import logging
from datetime import datetime

from agent.models import WebhookTrigger, AgentResponse
from agent.memory import MemoryStore
from agent.tools import MCPClient
from agent.graph import AgentGraph

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
memory_store: MemoryStore = None
mcp_client: MCPClient = None
agent_graph: AgentGraph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global memory_store, mcp_client, agent_graph
    
    # Startup
    logger.info("Starting autonomous agent...")
    
    # Initialize memory store
    memory_store = MemoryStore(
        db_path=os.getenv("MEMORY_DB_PATH", "./data/agent_memory.db"),
        json_path=os.getenv("MEMORY_JSON_PATH", "./data/agent_memory.json")
    )
    
    # Initialize MCP client
    mcp_client = MCPClient(
        mcp_host=os.getenv("MCP_HOST", "localhost"),
        mcp_port=int(os.getenv("MCP_PORT", 8001))
    )
    
    # Initialize agent graph
    agent_graph = AgentGraph(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        mcp_client=mcp_client
    )
    
    logger.info("Agent initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down agent...")


app = FastAPI(
    title="Autonomous AI Agent",
    description="AI agent with n8n triggers, LangGraph planning, and MCP tool execution",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "memory_initialized": memory_store is not None,
        "agent_initialized": agent_graph is not None
    }


@app.post("/webhook", response_model=AgentResponse)
async def handle_webhook(trigger: WebhookTrigger):
    """
    Main webhook endpoint for n8n triggers.
    
    Receives automation triggers, processes them through LangGraph,
    executes tools via MCP, and returns results.
    """
    start_time = time.time()
    logger.info(f"Received webhook trigger: {trigger.trigger_id} - {trigger.action}")
    
    try:
        # Get memory context
        context = memory_store.get_context()
        recent_convos = memory_store.get_recent_conversations(limit=5)
        
        # Enhance task with context
        task_description = f"""Action: {trigger.action}
Parameters: {trigger.parameters}
Context: {trigger.context}

Recent conversation history:
{recent_convos}

Memory context:
{context}
"""
        
        # Run agent workflow
        result = await agent_graph.run(task_description, context)
        
        # Save to memory
        memory_store.add_conversation(
            trigger_id=trigger.trigger_id,
            action=trigger.action,
            parameters=trigger.parameters,
            result=result,
            status="success" if result.get("status") == "success" else "error"
        )
        
        # Update context if needed
        if trigger.context:
            for key, value in trigger.context.items():
                memory_store.update_context(key, value)
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            trigger_id=trigger.trigger_id,
            status="success",
            result=result,
            execution_time=execution_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        
        # Save error to memory
        memory_store.add_conversation(
            trigger_id=trigger.trigger_id,
            action=trigger.action,
            parameters=trigger.parameters,
            result={"error": str(e)},
            status="error"
        )
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            trigger_id=trigger.trigger_id,
            status="error",
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.now()
        )


@app.get("/memory/conversations")
async def get_conversations(limit: int = 10):
    """Get recent conversation history."""
    try:
        conversations = memory_store.get_recent_conversations(limit=limit)
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/context")
async def get_memory_context():
    """Get current memory context."""
    try:
        context = memory_store.get_context()
        facts = memory_store.get_facts()
        return {
            "context": context,
            "facts": facts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    try:
        from agent.tools import AVAILABLE_TOOLS
        return {
            "tools": [
                {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
                for name, info in AVAILABLE_TOOLS.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("AGENT_HOST", "0.0.0.0"),
        port=int(os.getenv("AGENT_PORT", 8000))
    )
