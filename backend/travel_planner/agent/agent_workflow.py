from travel_planner.utils.model_loader import ModelLoader
from travel_planner.prompts.prompt_templates import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from travel_planner.tools.weather import get_weather
from travel_planner.tools.iternaryplaces import search_attractions, search_restaurants, search_hotels, search_activities
from travel_planner.tools.calculator import calculator
from travel_planner.tools.formatting import format_response
from travel_planner.tools.budget_validator import validate_budget
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

class GraphBuilder():
    def __init__(self, model_provider: str = "groq"):
        self.model_loader = ModelLoader(provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        # WHY: All available tools for the agent
        # Calculator: for budget calculations and cost summation
        # Formatter: for creating beautiful, emoji-rich responses
        # Budget Validator: CRITICAL for enforcing budget constraints
        self.tools = [
            get_weather,
            search_attractions,
            search_restaurants,
            search_hotels,
            search_activities,
            calculator,           # Budget calculations
            format_response,      # Beautiful output formatting
            validate_budget       # Budget enforcement - MUST use when user gives budget!
        ]
        
        # WHY: LangGraph's ToolNode automatically executes tools in parallel when possible
        # This is a built-in performance optimization - no additional code needed
        # Note: Tool-level timeouts are handled in individual tool implementations (10s each)
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        # WHY: Conversation memory allows agent to remember previous messages
        # SqliteSaver persists conversations to disk, surviving server restarts
        # Each conversation has a unique thread_id (session_id)
        self._setup_memory()
        
        self.graph = None
        
        self.system_prompt = SystemMessage(content=SYSTEM_PROMPT)
    
    def _setup_memory(self):
        """Setup persistent conversation memory using SqliteSaver"""
        # Create data directory if it doesn't exist
        # WHY: Store checkpoints in organized location
        data_dir = os.path.join(os.path.dirname(__file__), '../../data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize SqliteSaver with database file
        # WHY: Persistent storage allows conversations to survive restarts
        db_path = os.path.join(data_dir, 'checkpoints.db')
        
        # Create a connection and initialize the saver
        # This is the correct way to use SqliteSaver
        conn = sqlite3.connect(db_path, check_same_thread=False)
        self.memory = SqliteSaver(conn)
    
    def agent_function(self, state: MessagesState):
        """Main agent function"""
        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question
        response = self.llm_with_tools.invoke(input_question)
        return {"messages": [response]}

    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("agent", END)
        
        # WHY: Pass checkpointer to enable conversation memory
        # This allows the agent to load previous messages for each thread_id
        self.graph = graph_builder.compile(checkpointer=self.memory)
        return self.graph
        
    def __call__(self):
        return self.build_graph()