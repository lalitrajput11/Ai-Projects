#!/bin/bash
# Build and run script - alternative to docker-compose

set -e

echo "=== Building Autonomous Agent Images ==="

# Build the main image
echo "Building agent image..."
docker build -t autonomous-agent:latest .

echo ""
echo "=== Images built successfully! ==="
echo ""
echo "To run the services:"
echo "  1. Start Ollama: ~/bin/ollama serve &"
echo "  2. Pull model: ~/bin/ollama pull llama3.2:3b"
echo "  3. Run MCP server: docker run -d --name mcp-server -p 8001:8001 -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/data:/app/data --env-file .env autonomous-agent:latest python -m mcp_server.server"
echo "  4. Run agent: docker run -d --name agent -p 8000:8000 --network host -v $(pwd)/data:/app/data -v /var/run/docker.sock:/var/run/docker.sock --env-file .env autonomous-agent:latest"
echo "  5. Check health: curl http://localhost:8000/health"
echo ""
echo "OR use the provided script: ./run.sh"
