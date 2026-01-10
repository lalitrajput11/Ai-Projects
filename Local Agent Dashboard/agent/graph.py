"""LangGraph state machine for agent workflow."""
from typing import Dict, Any, List, TypedDict, Annotated
import operator
import logging
import json
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from agent.tools import MCPClient, AVAILABLE_TOOLS

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State definition for LangGraph."""
    messages: Annotated[List[Dict[str, str]], operator.add]
    current_task: str
    plan: List[str]
    tool_results: Annotated[List[Dict[str, Any]], operator.add]
    iteration: int
    finished: bool


class AgentGraph:
    """LangGraph-based agent workflow."""
    
    def __init__(self, ollama_host: str, model: str, mcp_client: MCPClient):
        self.llm = ChatOllama(
            base_url=ollama_host,
            model=model,
            temperature=0.7
        )
        self.mcp_client = mcp_client
        self.graph = self._build_graph()
        logger.info(f"Agent graph initialized with model: {model}")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("reflect", self._reflect_node)
        
        # Define edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "reflect")
        
        # Conditional edge from reflect
        workflow.add_conditional_edges(
            "reflect",
            self._should_continue,
            {
                "continue": "plan",
                "end": END
            }
        )
        
        return workflow.compile()
    
    async def _plan_node(self, state: AgentState) -> Dict:
        """Planning node: Analyze task and create action plan."""
        logger.info("Planning node executing...")
        
        # Get available tools
        tool_descriptions = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in AVAILABLE_TOOLS.items()
        ])
        
        # Create planning prompt
        prompt = f"""You are an autonomous AI agent. Your current task is:
{state['current_task']}

Available tools:
{tool_descriptions}

Previous results:
{json.dumps(state.get('tool_results', []), indent=2)}

Create a step-by-step plan to accomplish this task. Be specific and practical.
Output your plan as a numbered list."""

        try:
            response = await self.llm.ainvoke(prompt)
            plan_text = response.content
            
            # Parse plan into steps
            plan_steps = [
                line.strip() for line in plan_text.split('\n')
                if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 20))
            ]
            
            logger.info(f"Generated plan: {plan_steps}")
            
            return {
                "plan": plan_steps,
                "messages": [{"role": "assistant", "content": f"Plan: {plan_text}"}]
            }
        except Exception as e:
            logger.error(f"Planning error: {e}")
            return {
                "plan": ["Error in planning"],
                "messages": [{"role": "assistant", "content": f"Planning error: {str(e)}"}]
            }
    
    async def _execute_node(self, state: AgentState) -> Dict:
        """Execution node: Execute the plan using available tools."""
        logger.info("Execution node executing...")
        
        if not state.get('plan'):
            return {"tool_results": [{"error": "No plan available"}]}
        
        # Get current step
        current_iteration = state.get('iteration', 0)
        if current_iteration >= len(state['plan']):
            return {"finished": True}
        
        current_step = state['plan'][current_iteration]
        
        # Determine which tool to use
        prompt = f"""Based on this step: "{current_step}"

Available tools: {', '.join(AVAILABLE_TOOLS.keys())}

Which tool should be used? Respond with ONLY the tool name and parameters in JSON format.
Example: {{"tool": "docker_list_containers", "parameters": {{}}}}"""

        try:
            response = await self.llm.ainvoke(prompt)
            tool_decision = json.loads(response.content.strip())
            
            tool_name = tool_decision.get('tool')
            parameters = tool_decision.get('parameters', {})
            
            if tool_name in AVAILABLE_TOOLS:
                # Execute tool
                tool_func = AVAILABLE_TOOLS[tool_name]['function']
                result = await tool_func(self.mcp_client, **parameters)
                
                logger.info(f"Tool {tool_name} executed: {result}")
                
                return {
                    "tool_results": [{
                        "step": current_step,
                        "tool": tool_name,
                        "result": result
                    }],
                    "iteration": current_iteration + 1
                }
            else:
                return {
                    "tool_results": [{
                        "step": current_step,
                        "error": f"Unknown tool: {tool_name}"
                    }],
                    "iteration": current_iteration + 1
                }
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "tool_results": [{
                    "step": current_step,
                    "error": str(e)
                }],
                "iteration": current_iteration + 1
            }
    
    async def _reflect_node(self, state: AgentState) -> Dict:
        """Reflection node: Evaluate results and decide next action."""
        logger.info("Reflection node executing...")
        
        # Check if we've completed all steps or hit max iterations
        max_iterations = 10
        current_iteration = state.get('iteration', 0)
        
        if current_iteration >= len(state.get('plan', [])) or current_iteration >= max_iterations:
            return {"finished": True}
        
        # Analyze recent results
        recent_results = state.get('tool_results', [])[-3:]
        
        prompt = f"""Review the recent execution results:
{json.dumps(recent_results, indent=2)}

Current iteration: {current_iteration} of max {max_iterations}
Remaining steps: {len(state.get('plan', [])) - current_iteration}

Should we continue with the plan or are we done? Respond with "CONTINUE" or "DONE"."""

        try:
            response = await self.llm.ainvoke(prompt)
            decision = response.content.strip().upper()
            
            if "DONE" in decision:
                return {"finished": True}
            
            return {"finished": False}
        except Exception as e:
            logger.error(f"Reflection error: {e}")
            return {"finished": True}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if workflow should continue."""
        if state.get('finished', False):
            return "end"
        return "continue"
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the agent workflow."""
        initial_state = {
            "messages": [{"role": "user", "content": task}],
            "current_task": task,
            "plan": [],
            "tool_results": [],
            "iteration": 0,
            "finished": False
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            return {
                "status": "success",
                "results": final_state.get('tool_results', []),
                "plan": final_state.get('plan', []),
                "messages": final_state.get('messages', [])
            }
        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
