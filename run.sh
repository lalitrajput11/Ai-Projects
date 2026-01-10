#!/bin/bash
# Run the autonomous agent system

set -e

echo "=== Starting Autonomous Agent System ==="

# Check if Ollama is running
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running!"
    echo "Start it with: ~/bin/ollama serve &"
    echo "Then pull model: ~/bin/ollama pull llama3.2:3b"
    exit 1
fi
echo "✓ Ollama is running"

# Stop existing containers if any
echo "Stopping existing containers..."
docker stop mcp-server agent 2>/dev/null || true
docker rm mcp-server agent 2>/dev/null || true

# Create data directory
mkdir -p data

# Start MCP server
echo "Starting MCP server..."
docker run -d \
    --name mcp-server \
    --restart unless-stopped \
    -p 8001:8001 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$(pwd)/data:/app/data" \
    -e MCP_HOST=0.0.0.0 \
    -e MCP_PORT=8001 \
    -e LOG_LEVEL=INFO \
    -e DOCKER_HOST=unix:///var/run/docker.sock \
    --memory="1g" \
    --memory-reservation="512m" \
    autonomous-agent:latest \
    python -m mcp_server.server

# Wait for MCP server to start
sleep 3

# Start Agent
echo "Starting Agent..."
docker run -d \
    --name agent \
    --restart unless-stopped \
    -p 8000:8000 \
    --network host \
    -v "$(pwd)/data:/app/data" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e OLLAMA_HOST=http://localhost:11434 \
    -e OLLAMA_MODEL=llama3.2:3b \
    -e AGENT_HOST=0.0.0.0 \
    -e AGENT_PORT=8000 \
    -e MCP_HOST=localhost \
    -e MCP_PORT=8001 \
    -e MEMORY_DB_PATH=/app/data/agent_memory.db \
    -e MEMORY_JSON_PATH=/app/data/agent_memory.json \
    -e LOG_LEVEL=INFO \
    -e DOCKER_HOST=unix:///var/run/docker.sock \
    --memory="4g" \
    --memory-reservation="2g" \
    autonomous-agent:latest

# Wait for services to start
sleep 5

echo ""
echo "=== Services Started ==="
echo ""
echo "Checking health..."
curl -s http://localhost:8001/health && echo " ✓ MCP Server: http://localhost:8001"
curl -s http://localhost:8000/health && echo " ✓ Agent: http://localhost:8000"

echo ""
echo "=== System Ready! ==="
echo ""
echo "View logs:"
echo "  docker logs -f agent"
echo "  docker logs -f mcp-server"
echo ""
echo "Test webhook:"
echo '  curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d '"'"'{"trigger_id":"test-001","action":"list docker containers","parameters":{},"context":{}}'"'"''
echo ""
echo "Stop services:"
echo "  docker stop agent mcp-server"
