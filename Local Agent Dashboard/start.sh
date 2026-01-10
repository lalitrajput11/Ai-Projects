#!/bin/bash
# Quick Start Script - Run the Autonomous Agent

set -e

echo "=== Autonomous AI Agent - Quick Start ==="
echo ""

# Step 1: Start Ollama
echo "1. Starting Ollama..."
if pgrep -x "ollama" > /dev/null; then
    echo "   ✓ Ollama already running"
else
    ~/bin/ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo "   ✓ Ollama started (logs: /tmp/ollama.log)"
fi

# Step 2: Check/Pull Model
echo ""
echo "2. Checking Ollama model..."
if ~/bin/ollama list | grep -q "llama3.2:3b"; then
    echo "   ✓ llama3.2:3b is available"
else
    echo "   Pulling llama3.2:3b (this may take a while)..."
    ~/bin/ollama pull llama3.2:3b
fi

# Step 3: Start MCP Server
echo ""
echo "3. Starting MCP Server..."
source venv/bin/activate
python -m mcp_server.server > /tmp/mcp_server.log 2>&1 &
MCP_PID=$!
sleep 2
echo "   ✓ MCP Server started (PID: $MCP_PID, logs: /tmp/mcp_server.log)"

# Step 4: Start Agent
echo ""
echo "4. Starting Agent..."
python -m agent.main > /tmp/agent.log 2>&1 &
AGENT_PID=$!
sleep 3
echo "   ✓ Agent started (PID: $AGENT_PID, logs: /tmp/agent.log)"

# Step 5: Health Check
echo ""
echo "5. Health Check..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "   ✓ MCP Server: http://localhost:8001/health"
else
    echo "   ✗ MCP Server not responding"
fi

if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✓ Agent: http://localhost:8000/health"
else
    echo "   ✗ Agent not responding"
fi

echo ""
echo "=== System Ready! ==="
echo ""
echo "📝 View logs:"
echo "   tail -f /tmp/agent.log"
echo "   tail -f /tmp/mcp_server.log"
echo "   tail -f /tmp/ollama.log"
echo ""
echo "🧪 Test the agent (see QUICKSTART.md for examples)"
echo ""
echo "🛑 Stop services:"
echo "   kill $AGENT_PID $MCP_PID"
echo "   pkill ollama"
