# 🤖 Local Autonomous AI Agent

**A 100% local, offline-capable AI agent that plans, executes tools, and remembers.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)
![Ollama](https://img.shields.io/badge/ollama-local-orange.svg)

## 📖 Overview

This is a **Local Autonomous Agent** designed to run entirely on your own hardware. It leverages **Ollama** for its brain (LLM), **LangGraph** for planning and task decomposition, and **MCP (Model Context Protocol)** to safely execute tools like Docker management and filesystem operations.

It features a modern **Streamlit Dashboard** for monitoring, task submission, and memory visualization.

### Why this agent?
- **🔒 Privacy First**: All data stays on your machine. No API keys required for the LLM.
- **🧠 Persistent Memory**: Remembers past conversations and facts using SQLite + JSON.
- **🛠️ Extensible Tools**: Uses the standard Model Context Protocol (MCP) for tool definitions.
- **⚡ Fast & Local**: Optimized for local execution with models like `llama3.2` or `phi3`.

---

## ✨ Features

- **Dashboard UI**: A beautiful, dark-themed interface built with Streamlit.
- **Autonomous Planning**: Breaks down complex tasks into executable steps.
- **Tool Use**:
  - **Docker**: List, inspect, start, stop, and manage containers.
  - **Filesystem**: Read, write, list, and manage files.
- **Webhook Triggers**: Integrate with **n8n** or any webhook provider to trigger automations.
- **Resource Efficient**: designed to run on consumer hardware (16GB RAM recommended).

---

## 🏗️ Architecture

```mermaid
graph TD
    User[User / n8n] -->|Trigger| API[FastAPI Agent]
    User -->|Interact| UI[Streamlit Dashboard]
    UI -->|API Calls| API
    
    subgraph "Local Autonomous Agent"
        API -->|Plan & Execute| Brain[LangGraph Workflow]
        Brain -->|Inference| LLM[Ollama (Llama 3.2)]
        Brain -->|Store/Retrieve| Memory[(SQLite + JSON)]
        Brain -->|Execute Tools| MCP[MCP Server]
        
        MCP -->|Manage| Docker[Docker Engine]
        MCP -->|Manage| FS[Filesystem]
    end
```

---

## 🚀 Installation & Running Guide

Choose your operating system or preferred method below.

### Prerequisites (All Platforms)
1.  **Ollama**: Installed and running ([Download](https://ollama.com)).
2.  **Pull Model**: Run `ollama pull llama3.2:3b` in your terminal.
3.  **Git**: To clone the repository.

### 🐳 Method 1: Docker (Recommended for All OS)

This is the easiest way to ensure all dependencies and services work correctly.

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/yourusername/local-autonomous-agent.git
    cd local-autonomous-agent
    ```

2.  **Configure Environment**:
    copy `.env.example` to `.env`. Ensure `OLLAMA_HOST` is set to `http://host.docker.internal:11434`.

3.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build -d
    ```

4.  **Access Dashboard**: Open [http://localhost:8501](http://localhost:8501).

---

### 🐧 Method 2: Ubuntu Linux CLI (Native)

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/yourusername/local-autonomous-agent.git
    cd local-autonomous-agent
    ```

2.  **Set up Python Environment**:
    ```bash
    # Create virtual environment
    python3 -m venv venv
    
    # Activate it
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    ```bash
    cp .env.example .env
    # Edit .env and ensure OLLAMA_HOST=http://localhost:11434
    ```

4.  **Run Components (Open 3 separate terminals)**:

    *   **Terminal 1 (MCP Server)**:
        ```bash
        source venv/bin/activate
        python -m mcp_server.server
        ```

    *   **Terminal 2 (Agent API)**:
        ```bash
        source venv/bin/activate
        uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload
        ```

    *   **Terminal 3 (UI)**:
        ```bash
        source venv/bin/activate
        streamlit run streamlit_app.py
        ```

---

### 🪟 Method 3: Windows (PowerShell)

*Note: You need Python installed and added to PATH.*

1.  **Clone Repository**:
    ```powershell
    git clone https://github.com/yourusername/local-autonomous-agent.git
    cd local-autonomous-agent
    ```

2.  **Set up Python Environment**:
    ```powershell
    # Create virtual environment
    python -m venv venv
    
    # Activate it
    .\venv\Scripts\Activate.ps1
    
    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Copy `.env.example` to `.env` and set `OLLAMA_HOST=http://localhost:11434`.

4.  **Run Components (Open 3 separate PowerShell windows)**:

    *   **Window 1 (MCP Server)**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        $env:PYTHONPATH="."
        python -m mcp_server.server
        ```

    *   **Window 2 (Agent API)**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        $env:OLLAMA_HOST="http://localhost:11434"
        uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload
        ```

    *   **Window 3 (UI)**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        streamlit run streamlit_app.py
        ```

---

## 🖥️ Using the Streamlit UI Interface

The Streamlit dashboard allows you to interact with your agent visually.

### 1. 🏠 Dashboard Home
- **Status Check**: Instantly see if the Agent, MCP Server, and Memory are connected and healthy.
- **Recent Activity**: A feed of the latest tasks executed, showing triggered actions and statuses.
- **System Info**: View configured API URLs and loaded models.

### 2. 📝 Submit Task
This is the main control center.
- **Trigger ID**: Auto-generated ID (or enter your own) to track the task.
- **Action Description**: Enter your command in plain English.
  - *Example*: "Check the `data/` folder and list files larger than 1MB."
  - *Example*: "Inspect the docker container named `redis-stack` and tell me its uptime."
- **Context/Params**: (Advanced) Pass JSON data if integrating with specific workflows.
- **Submit**: Click the rocket 🚀 button. The agent will plan and execute. Be patient, as local inference takes a moment!

### 3. 💾 Memory Viewer
One of the most powerful features.
- **Conversation History**: Browse past interactions. Click to expand and see exactly what tools were called and what the output was.
- **Memory Context**: See the "facts" the agent has learned and stored in its long-term memory about your environment or preferences.

### 4. 🔧 Tools & Monitoring
- **Tools List**: Browse all available tools (Docker, Filesystem) to know what capabilities your agent has.
- **Real-time Logs**: See the raw output logs directly in the UI if configured, or use the provided terminal commands.

---

## 🔌 API Integration

You can interact with the agent programmatically via HTTP.

### Health Check
```bash
curl http://localhost:8000/health
```

### Trigger a Task via Webhook (e.g., from n8n)
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "trigger_id": "auto-001",
    "action": "Check if a file named report.txt exists",
    "parameters": {},
    "context": {"source": "script"}
  }'
```

---

## 📂 Project Structure

```
.
├── agent/                  # 🧠 Core Agent Logic
│   ├── main.py            # FastAPI Entrypoint
│   ├── graph.py           # LangGraph Workflow Definition
│   ├── memory.py          # Long-term Memory Management
│   └── tools.py           # Tool Interface Layer
├── mcp_server/            # 🛠️ Tool Execution Engine
│   ├── server.py          # MCP Server
│   └── *_tools.py         # Specific tool implementations
├── streamlit_app.py       # 🎨 Web Dashboard Source
├── data/                  # 💾 Persistent Storage (DBs, Logs)
├── docker-compose.yml     # 🐳 Container Orchestration
└── Dockerfile             # 📦 Agent Container Definition
```

---

## 🤝 Contributing

Contributions are welcome!
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<center>
    Made with ❤️ by Lalit Rajput
</center>
