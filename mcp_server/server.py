"""MCP server implementation."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import logging

from mcp_server.docker_tools import DockerTools
from mcp_server.filesystem_tools import FilesystemTools

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol server for tool execution",
    version="1.0.0"
)

# Initialize tools
docker_tools = DockerTools()
filesystem_tools = FilesystemTools(base_path="/app/data")


class ToolRequest(BaseModel):
    """Generic tool request model."""
    parameters: Optional[Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MCP Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/tools")
async def list_tools():
    """List all available tools."""
    return {
        "tools": [
            "docker_list",
            "docker_exec",
            "docker_logs",
            "docker_inspect",
            "filesystem_read",
            "filesystem_write",
            "filesystem_list",
            "filesystem_delete",
            "filesystem_exists"
        ]
    }


# Docker Tools Endpoints
@app.post("/tools/docker_list")
async def docker_list(request: ToolRequest):
    """List Docker containers."""
    all_containers = request.parameters.get("all", True)
    result = docker_tools.list_containers(all_containers=all_containers)
    return result


@app.post("/tools/docker_exec")
async def docker_exec(request: ToolRequest):
    """Execute command in Docker container."""
    container_id = request.parameters.get("container_id")
    command = request.parameters.get("command")
    
    if not container_id or not command:
        raise HTTPException(status_code=400, detail="Missing container_id or command")
    
    result = docker_tools.exec_command(container_id, command)
    return result


@app.post("/tools/docker_logs")
async def docker_logs(request: ToolRequest):
    """Get Docker container logs."""
    container_id = request.parameters.get("container_id")
    tail = request.parameters.get("tail", 100)
    
    if not container_id:
        raise HTTPException(status_code=400, detail="Missing container_id")
    
    result = docker_tools.get_logs(container_id, tail=tail)
    return result


@app.post("/tools/docker_inspect")
async def docker_inspect(request: ToolRequest):
    """Inspect Docker container."""
    container_id = request.parameters.get("container_id")
    
    if not container_id:
        raise HTTPException(status_code=400, detail="Missing container_id")
    
    result = docker_tools.inspect_container(container_id)
    return result


# Filesystem Tools Endpoints
@app.post("/tools/filesystem_read")
async def filesystem_read(request: ToolRequest):
    """Read file contents."""
    path = request.parameters.get("path")
    
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")
    
    result = filesystem_tools.read_file(path)
    return result


@app.post("/tools/filesystem_write")
async def filesystem_write(request: ToolRequest):
    """Write to file."""
    path = request.parameters.get("path")
    content = request.parameters.get("content")
    
    if not path or content is None:
        raise HTTPException(status_code=400, detail="Missing path or content")
    
    result = filesystem_tools.write_file(path, content)
    return result


@app.post("/tools/filesystem_list")
async def filesystem_list(request: ToolRequest):
    """List directory contents."""
    path = request.parameters.get("path", ".")
    result = filesystem_tools.list_directory(path)
    return result


@app.post("/tools/filesystem_delete")
async def filesystem_delete(request: ToolRequest):
    """Delete file."""
    path = request.parameters.get("path")
    
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")
    
    result = filesystem_tools.delete_file(path)
    return result


@app.post("/tools/filesystem_exists")
async def filesystem_exists(request: ToolRequest):
    """Check if file exists."""
    path = request.parameters.get("path")
    
    if not path:
        raise HTTPException(status_code=400, detail="Missing path")
    
    result = filesystem_tools.file_exists(path)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", 8001))
    )
