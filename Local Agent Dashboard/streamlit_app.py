"""
Streamlit UI for Autonomous AI Agent
Provides web interface for task submission, monitoring, and memory viewing
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd

# Configuration
AGENT_URL = "http://localhost:8000"
MCP_URL = "http://localhost:8001"

# Page config
st.set_page_config(
    page_title="Autonomous AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .status-online {
        color: #00ff00;
        font-weight: bold;
    }
    .status-offline {
        color: #ff0000;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def check_service_health(url):
    """Check if service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_agent_health():
    """Get agent health status"""
    try:
        response = requests.get(f"{AGENT_URL}/health", timeout=2)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def get_tools():
    """Get available tools"""
    try:
        response = requests.get(f"{AGENT_URL}/tools", timeout=2)
        return response.json().get("tools", []) if response.status_code == 200 else []
    except:
        return []


def get_conversations(limit=10):
    """Get conversation history"""
    try:
        response = requests.get(f"{AGENT_URL}/memory/conversations?limit={limit}", timeout=5)
        return response.json().get("conversations", []) if response.status_code == 200 else []
    except:
        return []


def get_memory_context():
    """Get memory context"""
    try:
        response = requests.get(f"{AGENT_URL}/memory/context", timeout=2)
        return response.json() if response.status_code == 200 else {}
    except:
        return {}


def submit_task(trigger_id, action, parameters, context):
    """Submit task to agent"""
    try:
        payload = {
            "trigger_id": trigger_id,
            "action": action,
            "parameters": parameters,
            "context": context
        }
        response = requests.post(f"{AGENT_URL}/webhook", json=payload, timeout=300)
        return response.json() if response.status_code == 200 else {"error": "Request failed"}
    except Exception as e:
        return {"error": str(e)}


# Sidebar
with st.sidebar:
    st.markdown("## 🤖 Agent Control Panel")
    
    # Service Status
    st.markdown("### Service Status")
    agent_online = check_service_health(AGENT_URL)
    mcp_online = check_service_health(MCP_URL)
    
    if agent_online:
        st.markdown("**Agent**: <span class='status-online'>● Online</span>", unsafe_allow_html=True)
    else:
        st.markdown("**Agent**: <span class='status-offline'>● Offline</span>", unsafe_allow_html=True)
    
    if mcp_online:
        st.markdown("**MCP Server**: <span class='status-online'>● Online</span>", unsafe_allow_html=True)
    else:
        st.markdown("**MCP Server**: <span class='status-offline'>● Offline</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    st.markdown("### Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Dashboard", "📝 Submit Task", "💾 Memory Viewer", "🔧 Tools", "📊 Monitoring"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Quick Actions
    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()
    
    if st.button("📋 View Logs", use_container_width=True):
        st.info("Check terminal: tail -f /tmp/agent.log")


# Main Content
if page == "🏠 Dashboard":
    st.markdown("<div class='main-header'>🤖 Autonomous AI Agent Dashboard</div>", unsafe_allow_html=True)
    
    # Health Status
    health = get_agent_health()
    if health:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "✅ Healthy")
        with col2:
            st.metric("Memory Init", "✅" if health.get("memory_initialized") else "❌")
        with col3:
            st.metric("Agent Init", "✅" if health.get("agent_initialized") else "❌")
    else:
        st.error("⚠️ Agent is offline. Start with: `python -m agent.main`")
    
    st.divider()
    
    # Recent Activity
    st.subheader("📜 Recent Activity")
    conversations = get_conversations(5)
    
    if conversations:
        for conv in conversations:
            with st.expander(f"🔹 {conv.get('action', 'Unknown')} - {conv.get('trigger_id', 'N/A')}"):
                st.write(f"**Timestamp**: {conv.get('timestamp', 'N/A')}")
                st.write(f"**Status**: {conv.get('status', 'N/A')}")
                st.write(f"**Parameters**: {json.dumps(conv.get('parameters', {}), indent=2)}")
                if conv.get('result'):
                    st.json(conv['result'])
    else:
        st.info("No recent activity. Submit a task to get started!")
    
    st.divider()
    
    # System Info
    st.subheader("ℹ️ System Information")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Agent URL**: {AGENT_URL}  
        **MCP URL**: {MCP_URL}  
        **Model**: llama3.2:3b
        """)
    with col2:
        tools = get_tools()
        st.info(f"""
        **Available Tools**: {len(tools)}  
        **Memory**: SQLite + JSON  
        **Status**: {'Running' if agent_online else 'Stopped'}
        """)


elif page == "📝 Submit Task":
    st.markdown("<div class='main-header'>📝 Submit Task to Agent</div>", unsafe_allow_html=True)
    
    if not agent_online:
        st.error("⚠️ Agent is offline. Please start the agent first.")
        st.stop()
    
    # Task Form
    with st.form("task_form"):
        st.subheader("Task Details")
        
        trigger_id = st.text_input(
            "Trigger ID",
            value=f"ui-{int(time.time())}",
            help="Unique identifier for this task"
        )
        
        action = st.text_area(
            "Action/Task Description",
            placeholder="Example: List all docker containers and save count to a file",
            help="Describe what you want the agent to do"
        )
        
        st.subheader("Advanced Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            parameters = st.text_area(
                "Parameters (JSON)",
                value="{}",
                help="Additional parameters as JSON"
            )
        
        with col2:
            context = st.text_area(
                "Context (JSON)",
                value='{"source": "streamlit_ui"}',
                help="Additional context as JSON"
            )
        
        submitted = st.form_submit_button("🚀 Submit Task", use_container_width=True)
    
    if submitted:
        if not action:
            st.error("Please provide a task description!")
        else:
            with st.spinner("🔄 Submitting task to agent..."):
                try:
                    params = json.loads(parameters) if parameters else {}
                    ctx = json.loads(context) if context else {}
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")
                    st.stop()
                
                # Show submission
                st.info("📤 Task submitted. Agent is processing...")
                st.json({
                    "trigger_id": trigger_id,
                    "action": action,
                    "parameters": params,
                    "context": ctx
                })
                
                # Submit task (this will take time on CPU)
                with st.spinner("⏳ Agent is planning and executing... This may take 10-20 minutes on CPU"):
                    result = submit_task(trigger_id, action, params, ctx)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Task completed!")
                    st.subheader("📊 Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Status", result.get("status", "unknown"))
                        st.metric("Execution Time", f"{result.get('execution_time', 0):.2f}s")
                    with col2:
                        st.metric("Trigger ID", result.get("trigger_id", "N/A"))
                    
                    st.json(result)


elif page == "💾 Memory Viewer":
    st.markdown("<div class='main-header'>💾 Agent Memory Viewer</div>", unsafe_allow_html=True)
    
    if not agent_online:
        st.error("⚠️ Agent is offline. Please start the agent first.")
        st.stop()
    
    tab1, tab2 = st.tabs(["📜 Conversation History", "🧠 Memory Context"])
    
    with tab1:
        st.subheader("Conversation History")
        
        limit = st.slider("Number of conversations", 5, 50, 10)
        conversations = get_conversations(limit)
        
        if conversations:
            # Create DataFrame
            df_data = []
            for conv in conversations:
                df_data.append({
                    "Trigger ID": conv.get("trigger_id", "N/A"),
                    "Action": conv.get("action", "Unknown"),
                    "Status": conv.get("status", "unknown"),
                    "Timestamp": conv.get("timestamp", "N/A")
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            
            # Detailed view
            st.subheader("Detailed Conversation View")
            for idx, conv in enumerate(conversations):
                with st.expander(f"{idx+1}. {conv.get('action', 'Unknown')} ({conv.get('trigger_id', 'N/A')})"):
                    st.write(f"**Timestamp**: {conv.get('timestamp')}")
                    st.write(f"**Status**: {conv.get('status')}")
                    
                    st.write("**Parameters**:")
                    st.json(conv.get("parameters", {}))
                    
                    st.write("**Result**:")
                    st.json(conv.get("result", {}))
        else:
            st.info("No conversations found. Submit a task to create history!")
    
    with tab2:
        st.subheader("Memory Context")
        
        memory = get_memory_context()
        
        if memory:
            context = memory.get("context", {})
            facts = memory.get("facts", [])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Context Keys", len(context))
                if context:
                    st.json(context)
                else:
                    st.info("No context stored yet")
            
            with col2:
                st.metric("Stored Facts", len(facts))
                if facts:
                    for i, fact in enumerate(facts, 1):
                        st.write(f"{i}. {fact}")
                else:
                    st.info("No facts stored yet")
        else:
            st.info("No memory data available")


elif page == "🔧 Tools":
    st.markdown("<div class='main-header'>🔧 Available Tools</div>", unsafe_allow_html=True)
    
    if not agent_online:
        st.error("⚠️ Agent is offline. Please start the agent first.")
        st.stop()
    
    tools = get_tools()
    
    if tools:
        st.info(f"**Total Tools**: {len(tools)}")
        
        # Docker Tools
        st.subheader("🐳 Docker Tools")
        docker_tools = [t for t in tools if t["name"].startswith("docker")]
        for tool in docker_tools:
            with st.expander(f"📌 {tool['name']}"):
                st.write(f"**Description**: {tool.get('description', 'N/A')}")
                st.write("**Parameters**:")
                st.json(tool.get("parameters", {}))
        
        # Filesystem Tools
        st.subheader("📁 Filesystem Tools")
        fs_tools = [t for t in tools if t["name"].startswith("filesystem")]
        for tool in fs_tools:
            with st.expander(f"📌 {tool['name']}"):
                st.write(f"**Description**: {tool.get('description', 'N/A')}")
                st.write("**Parameters**:")
                st.json(tool.get("parameters", {}))
    else:
        st.warning("No tools available. Check if agent is running.")


elif page == "📊 Monitoring":
    st.markdown("<div class='main-header'>📊 Real-time Monitoring</div>", unsafe_allow_html=True)
    
    st.info("💡 **Tip**: Open terminal and run `tail -f /tmp/agent.log` to see real-time logs")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto-refresh (every 10s)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        agent_status = "🟢 Online" if agent_online else "🔴 Offline"
        st.metric("Agent Status", agent_status)
    
    with col2:
        mcp_status = "🟢 Online" if mcp_online else "🔴 Offline"
        st.metric("MCP Server", mcp_status)
    
    with col3:
        conversations = get_conversations(100)
        st.metric("Total Tasks", len(conversations))
    
    st.divider()
    
    # Recent tasks chart
    if conversations:
        st.subheader("Task Status Distribution")
        
        status_counts = {}
        for conv in conversations:
            status = conv.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.bar_chart(status_counts)
    
    st.divider()
    
    # System commands
    st.subheader("🖥️ Useful Commands")
    
    st.code("""
# View agent logs
tail -f /tmp/agent.log

# View MCP server logs
tail -f /tmp/mcp_server.log

# View Ollama logs
tail -f /tmp/ollama.log

# Check running processes
ps aux | grep -E "(ollama|agent|mcp)"

# Monitor memory
free -h
    """, language="bash")
    
    if auto_refresh:
        time.sleep(10)
        st.rerun()


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    🤖 Autonomous AI Agent with LangGraph | Made By Lalit Rajput |
    Powered by Ollama (llama3.2:3b) | 
    100% Offline
</div>
""", unsafe_allow_html=True)
