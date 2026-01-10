# 🚀 Local Autonomous Agent Journey & Documentation

## 🌟 What Are We Doing Here?
We are building a **Local Autonomous AI Agent** that runs entirely on your local machine. It allows you to:
1.  **Plan and Execute Tasks**: The agent uses an LLM (via Ollama) to break down complex instructions into a step-by-step plan.
2.  **Interact with Your System**: Through the **Model Context Protocol (MCP)**, it can safely execute commands, manage Docker containers, and manipulate files.
3.  **Visual Management**: A beautiful **Streamlit Dashboard** provides a user-friendly interface to control the agent, view its "thought process," and manage its memory.
4.  **Privacy**: Everything runs 100% offline. No data leaves your computer.

---

## 🗺️ The Journey: How We Created This Project
This project evolved through several key stages to become a robust local agent system:

### 1. **The Spark (Concept)**
We started with the idea of running an autonomous agent locally without relying on expensive and privacy-invasive cloud APIs. The goal: A system that can "think" and "do" on a standard consumer laptop.

### 2. **The Brain (Ollama & LangGraph)**
- We chose **Ollama** as the local inference engine to run models like `llama3.2` or `phi3`.
- We implemented **LangGraph** to give the agent a structured "brain." Instead of just generating text, the agent follows a strict state machine: **Plan → Execute → Reflect**. This ensures it stays on track and corrects its own mistakes.

### 3. **The Hands (MCP Server)**
An agent is useless if it can't touch the world. We adopted the **Model Context Protocol (MCP)**, a standard for connecting AI to tools.
- We built a custom `mcp_server` that acts as a secure bridge.
- We implemented specific toolsets:
    - **Docker Tools**: To manage containers (start, stop, inspect).
    - **Filesystem Tools**: To read/write files and list directories.

### 4. **The Face (Streamlit Dashboard)**
To make it accessible, we built a polished UI using **Streamlit**.
- It visualizes the agent's memory (SQLite).
- It shows real-time logs of the agent's actions.
- It provides a simple chat interface to submit tasks.

---

## 🏃 How to Run It

### Option 1: Docker (Recommended)
This is the easiest method as it handles all dependencies for you.
1.  **Clone** the repo.
2.  **Configure `.env`**: Copy `.env.example` to `.env` and set `OLLAMA_HOST=http://host.docker.internal:11434`.
3.  **Run**:
    ```bash
    docker-compose up --build -d
    ```
4.  **Open**: Go to [http://localhost:8501](http://localhost:8501).

### Option 2: Run Locally (Linux/Mac)
If you want to run it natively for development:

1.  **Start the MCP Server** (Terminal 1):
    ```bash
    source venv/bin/activate
    python -m mcp_server.server
    ```

2.  **Start the Agent API** (Terminal 2):
    ```bash
    source venv/bin/activate
    uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload
    ```

3.  **Start the UI** (Terminal 3):
    ```bash
    source venv/bin/activate
    streamlit run streamlit_app.py
    ```

---

## 📂 File Importance & Project Structure

Here is a breakdown of the key files and directories:

### Core Definitions
-   **`README.md`**: The main entry point for documentation, features, and setup.
-   **`docker-compose.yml`**: Defines how the Agent, UI, and Database services spin up together.
-   **`.env`**: Stores sensitive configuration like API URLs (keep this secret!).

### `agent/` (The Brain)
-   **`graph.py`**: **CRITICAL**. This defines the LangGraph workflow (`Plan` -> `Execute` -> `Reflect`). It controls the logic flow.
-   **`main.py`**: The FastAPI server that receives requests (from UI or webhooks) and starts the graph execution.
-   **`memory.py`**: Handles long-term storage (SQLite) so the agent "remembers" past interactions.
-   **`tools.py`**: The client-side code that talks to the MCP server.

### `mcp_server/` (The Hands)
-   **`server.py`**: The server that listens for tool execution requests.
-   **`docker_tools.py`**: Actual python code to interact with the Docker daemon.
-   **`filesystem_tools.py`**: Actual python code to read/write files safely.

### `data/`
-   Stores the SQLite database and any files the agent generates.

---

## 🔄 Workflow Structure

The agent follows a cyclic loop defined in `agent/graph.py`:

```mermaid
graph TD
    Start([User Request]) --> Plan
    
    Plan[📝 Plan Node] -->|Generate Steps| Execute
    
    Execute[🔨 Execute Node] -->|Run Tool (MCP)| Reflect
    
    Reflect[🤔 Reflect Node] -->|Task Complete?| Done([Finish])
    Reflect -->|More Steps Needed?| Plan
```

1.  **Plan**: The LLM analyzes the user request and available tools, generating a numbered list of steps.
2.  **Execute**: The Agent picks the current step, decides which tool to call (e.g., `docker_list`), and sends the command to the MCP server.
3.  **Reflect**: The Agent looks at the tool output. Did it work? Do we need to update the plan? If not finished, it loops back.

---

## 🧩 Program Design
The system uses significant **Separation of Concerns**:
-   **Frontend (Streamlit)**: Only displays data and sends HTTP requests. It contains no business logic.
-   **Backend (FastAPI)**: Handles request orchestration and runs the LangGraph loop.
-   **Tool/MCP Layer**: Runs as a separate process (could even be on a different machine). This is a security feature—if the tool server crashes, the agent brain survives.

---

## ⚡ Integration with n8n (Automation)

You can easily trigger this agent from **n8n** to automate physical workflows based on external triggers (e.g., an email or Slack message).

### Setup in n8n
1.  **Node**: Use an **HTTP Request** node.
2.  **Method**: `POST`
3.  **URL**: `http://<your-agent-ip>:8000/webhook` (Use `http://host.docker.internal:8000/webhook` if n8n is also in Docker).
4.  **Authentication**: None (unless you added it).
5.  **Headers**:
    -   `Content-Type`: `application/json`
6.  **Body**:
    ```json
    {
      "trigger_id": "n8n-{{$execution.id}}",
      "action": "Check the status of the 'web-server' container and restart it if it is down.",
      "parameters": {},
      "context": {
        "source": "n8n_automation"
      }
    }
    ```

### Example Use Case
1.  **Trigger**: n8n receives a webhook from GitHub (e.g., "New Issue Created").
2.  **Action**: n8n calls your Local Agent.
3.  **Agent**: "Reads the issue -> Checks the code in the filesystem -> Runs a test docker container".
4.  **Result**: The Agent logs the result, which you can see in the Dashboard.
