"""Filesystem tools for MCP server."""
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FilesystemTools:
    """Filesystem operations."""
    
    def __init__(self, base_path: str = "/app/data"):
        self.base_path = Path(base_path)
        logger.info(f"Filesystem tools initialized with base path: {base_path}")
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve and validate path."""
        resolved = (self.base_path / path).resolve()
        # Ensure path is within base_path for security
        if not str(resolved).startswith(str(self.base_path)):
            raise ValueError(f"Path {path} is outside allowed directory")
        return resolved
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents."""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {"error": f"File not found: {path}"}
            
            if not file_path.is_file():
                return {"error": f"Not a file: {path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file: {path}")
            return {
                "content": content,
                "size": file_path.stat().st_size,
                "path": str(file_path)
            }
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"error": str(e)}
    
    def write_file(self, path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
        """Write content to file."""
        try:
            file_path = self._resolve_path(path)
            
            # Create parent directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote file: {path}")
            return {
                "success": True,
                "path": str(file_path),
                "size": len(content)
            }
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return {"error": str(e)}
    
    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """List directory contents."""
        try:
            dir_path = self._resolve_path(path)
            
            if not dir_path.exists():
                return {"error": f"Directory not found: {path}"}
            
            if not dir_path.is_dir():
                return {"error": f"Not a directory: {path}"}
            
            files = []
            for item in dir_path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "file" if item.is_file() else "directory",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            logger.info(f"Listed directory: {path} ({len(files)} items)")
            return {"files": files, "path": str(dir_path)}
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {"error": str(e)}
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file."""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {"error": f"File not found: {path}"}
            
            if not file_path.is_file():
                return {"error": f"Not a file: {path}"}
            
            file_path.unlink()
            logger.info(f"Deleted file: {path}")
            return {"success": True, "path": str(file_path)}
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error deleting file {path}: {e}")
            return {"error": str(e)}
    
    def file_exists(self, path: str) -> Dict[str, Any]:
        """Check if file exists."""
        try:
            file_path = self._resolve_path(path)
            exists = file_path.exists()
            
            return {
                "exists": exists,
                "path": str(file_path),
                "is_file": file_path.is_file() if exists else None,
                "is_directory": file_path.is_dir() if exists else None
            }
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error checking file {path}: {e}")
            return {"error": str(e)}
