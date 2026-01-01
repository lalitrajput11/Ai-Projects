"""Tool definitions and MCP client integration."""
from typing import Dict, Any, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP server."""
    
    def __init__(self, mcp_host: str, mcp_port: int):
        self.base_url = f"http://{mcp_host}:{mcp_port}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool via MCP server."""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=parameters
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def list_tools(self) -> List[str]:
        """List available tools."""
        try:
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json().get("tools", [])
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []


# Tool definitions for LangChain
async def docker_list_containers(mcp_client: MCPClient, **kwargs) -> str:
    """List Docker containers."""
    result = await mcp_client.call_tool("docker_list", kwargs)
    if "error" in result:
        return f"Error: {result['error']}"
    containers = result.get("containers", [])
    return f"Found {len(containers)} containers: {containers}"


async def docker_exec_command(mcp_client: MCPClient, container_id: str, command: str, **kwargs) -> str:
    """Execute command in Docker container."""
    result = await mcp_client.call_tool("docker_exec", {
        "container_id": container_id,
        "command": command
    })
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Command output: {result.get('output', '')}"


async def filesystem_read(mcp_client: MCPClient, path: str, **kwargs) -> str:
    """Read file contents."""
    result = await mcp_client.call_tool("filesystem_read", {"path": path})
    if "error" in result:
        return f"Error: {result['error']}"
    return f"File contents: {result.get('content', '')}"


async def filesystem_write(mcp_client: MCPClient, path: str, content: str, **kwargs) -> str:
    """Write to file."""
    result = await mcp_client.call_tool("filesystem_write", {
        "path": path,
        "content": content
    })
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Successfully wrote to {path}"


async def filesystem_list(mcp_client: MCPClient, path: str, **kwargs) -> str:
    """List directory contents."""
    result = await mcp_client.call_tool("filesystem_list", {"path": path})
    if "error" in result:
        return f"Error: {result['error']}"
    files = result.get("files", [])
    return f"Found {len(files)} items: {files}"


# Tool registry
AVAILABLE_TOOLS = {
    "docker_list_containers": {
        "function": docker_list_containers,
        "description": "List all Docker containers (running and stopped)",
        "parameters": {}
    },
    "docker_exec_command": {
        "function": docker_exec_command,
        "description": "Execute a command inside a Docker container",
        "parameters": {
            "container_id": "ID of the container",
            "command": "Command to execute"
        }
    },
    "filesystem_read": {
        "function": filesystem_read,
        "description": "Read contents of a file",
        "parameters": {
            "path": "Path to the file"
        }
    },
    "filesystem_write": {
        "function": filesystem_write,
        "description": "Write content to a file",
        "parameters": {
            "path": "Path to the file",
            "content": "Content to write"
        }
    },
    "filesystem_list": {
        "function": filesystem_list,
        "description": "List contents of a directory",
        "parameters": {
            "path": "Path to the directory"
        }
    }
}
