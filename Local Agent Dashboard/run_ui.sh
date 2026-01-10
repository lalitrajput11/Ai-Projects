#!/bin/bash
# Start the Streamlit UI for Autonomous Agent

set -e

echo "=== Starting Streamlit UI for Autonomous Agent ==="
echo ""

# Check if agent is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Agent is not running!"
    echo ""
    echo "Start the agent first:"
    echo "  ./start.sh"
    echo "  # OR"
    echo "  source venv/bin/activate && python -m agent.main &"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting Streamlit UI..."
echo ""
echo "📱 Opening in browser at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Activate venv and run streamlit
source venv/bin/activate
streamlit run streamlit_app.py
