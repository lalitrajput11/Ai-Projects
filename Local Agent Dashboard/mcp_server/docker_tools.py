"""Docker tools for MCP server."""
import docker
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DockerTools:
    """Docker operations via Docker SDK."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
    
    def list_containers(self, all_containers: bool = True) -> Dict[str, Any]:
        """List Docker containers."""
        if not self.client:
            return {"error": "Docker client not initialized"}
        
        try:
            containers = self.client.containers.list(all=all_containers)
            container_list = [
                {
                    "id": c.id[:12],
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else c.image.id[:12]
                }
                for c in containers
            ]
            logger.info(f"Listed {len(container_list)} containers")
            return {"containers": container_list}
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return {"error": str(e)}
    
    def exec_command(self, container_id: str, command: str) -> Dict[str, Any]:
        """Execute command in a container."""
        if not self.client:
            return {"error": "Docker client not initialized"}
        
        try:
            container = self.client.containers.get(container_id)
            result = container.exec_run(command)
            
            output = result.output.decode('utf-8') if result.output else ""
            logger.info(f"Executed command in {container_id}: {command}")
            
            return {
                "exit_code": result.exit_code,
                "output": output
            }
        except docker.errors.NotFound:
            return {"error": f"Container {container_id} not found"}
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"error": str(e)}
    
    def get_logs(self, container_id: str, tail: int = 100) -> Dict[str, Any]:
        """Get container logs."""
        if not self.client:
            return {"error": "Docker client not initialized"}
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode('utf-8')
            logger.info(f"Retrieved logs from {container_id}")
            
            return {"logs": logs}
        except docker.errors.NotFound:
            return {"error": f"Container {container_id} not found"}
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return {"error": str(e)}
    
    def inspect_container(self, container_id: str) -> Dict[str, Any]:
        """Inspect container details."""
        if not self.client:
            return {"error": "Docker client not initialized"}
        
        try:
            container = self.client.containers.get(container_id)
            info = {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "created": container.attrs.get('Created'),
                "ports": container.attrs.get('NetworkSettings', {}).get('Ports', {})
            }
            logger.info(f"Inspected container {container_id}")
            
            return {"info": info}
        except docker.errors.NotFound:
            return {"error": f"Container {container_id} not found"}
        except Exception as e:
            logger.error(f"Error inspecting container: {e}")
            return {"error": str(e)}
