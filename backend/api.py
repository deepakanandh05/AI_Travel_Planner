"""
FastAPI server for AI Travel Planner frontend

WHY: Provides REST API endpoint for the React frontend with conversation memory
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from travel_planner.agent.agent_workflow import GraphBuilder
from travel_planner.core.validators import validate_user_input, validate_agent_output
from travel_planner.utils.logger import setup_logger
from dotenv import load_dotenv
import os
import time
import uuid
import json
import asyncio

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(title="AI Travel Planner API")

# CORS configuration
# WHY: Allow frontend running on different port to access API
# Support both local development and production URLs
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
graph_builder = None
graph = None
session_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent on server startup"""
    global graph_builder, graph
    
    logger.info("Initializing AI Travel Planner Agent")
    graph_builder = GraphBuilder(model_provider="gemini")
    graph = graph_builder()
    logger.info("Agent initialized successfully")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # WHY: Track conversation sessions

class ChatResponse(BaseModel):
    success: bool
    response: str = None
    session_id: str = None  # WHY: Return session ID to frontend
    error: str = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for frontend with conversation memory.
    
    WHY: Processes user queries through the AI agent with session-based memory
    Each session maintains its own conversation history
    """
    if not graph:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    user_message = request.message.strip()
    
    # Generate or use existing session ID
    # WHY: Session ID (thread_id) allows agent to load conversation history
    session_id = request.session_id or str(uuid.uuid4())
    
    # Input validation
    validation_result = validate_user_input(user_message)
    if not validation_result["valid"]:
        logger.warning(
            "Invalid user input",
            extra={
                "query": user_message[:100],
                "error": validation_result["error_message"],
                "success": False,
                "session_id": session_id
            }
        )
        return ChatResponse(
            success=False,
            error=validation_result["error_message"],
            session_id=session_id
        )
    
    # Process query
    start_time = time.time()
    tools_used = []
    
    try:
        logger.info("Processing user query", extra={"query": user_message, "session_id": session_id})
        
        # Create messages list for this request
        # WHY: With memory enabled, we only pass current message
        # Agent automatically loads previous messages from checkpointer via thread_id
        messages = [("user", user_message)]
        initial_state = {"messages": messages}
        
        # Invoke the agent with session config
        # WHY: thread_id tells checkpointer which conversation to load/save
        config = {"configurable": {"thread_id": session_id}}
        result = graph.invoke(initial_state, config=config)
        
        # Extract response
        last_message = result['messages'][-1]
        response_content = last_message.content
        
        # Handle Gemini's response format
        if isinstance(response_content, list):
            # Gemini returns list of content objects
            text_content = ""
            for item in response_content:
                if isinstance(item, dict) and 'text' in item:
                    text_content += item['text']
                elif isinstance(item, str):
                    text_content += item
            response_content = text_content
        elif not isinstance(response_content, str):
            response_content = str(response_content)
        
        # Track which tools were used
        for msg in result['messages']:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tools_used.extend([tc['name'] for tc in msg.tool_calls])
        
        # Output validation
        output_validation = validate_agent_output(response_content, user_message)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log success
        logger.info(
            "Successfully processed query",
            extra={
                "query": user_message[:100],
                "tools_used": list(set(tools_used)),
                "latency_ms": latency_ms,
                "success": True,
                "output_score": output_validation["score"],
                "session_id": session_id
            }
        )
        
        return ChatResponse(
            success=True,
            response=response_content,
            session_id=session_id
        )
        
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        
        logger.error(
            "Error processing query",
            extra={
                "query": user_message[:100],
                "tools_used": list(set(tools_used)),
                "errors": [error_msg],
                "latency_ms": latency_ms,
                "success": False,
                "session_id": session_id
            }
        )
        
        return ChatResponse(
            success=False,
            error=f"An error occurred: {error_msg}",
            session_id=session_id
        )

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint that shows agent reasoning in real-time
    
    WHY: Provides transparency and engagement by showing tool calls as they happen
    """
    if not graph:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    user_message = request.message.strip()
    session_id = request.session_id or str(uuid.uuid4())
    
    # Input validation
    validation_result = validate_user_input(user_message)
    if not validation_result["valid"]:
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': validation_result['error_message']})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events as agent processes"""
        try:
            # Send initial thinking event
            yield f"data: {json.dumps({'type': 'thinking', 'message': 'Starting to process your request...', 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.1)  # Small delay for UX
            
            # Create messages and config
            messages = [("user", user_message)]
            initial_state = {"messages": messages}
            config = {"configurable": {"thread_id": session_id}}
            
            # Stream events as the agent runs
            # LangGraph's .stream() yields intermediate results
            final_response = None
            tool_names = {
                'get_weather': 'Checking weather',
                'search_hotels': 'Searching for hotels',
                'search_restaurants': 'Finding restaurants',
                'search_attractions': 'Discovering attractions',
                'search_activities': 'Looking for activities',
                'calculator': 'Calculating costs',
                'validate_budget': 'Validating budget',
                'format_response': 'Formatting response'
            }
            
            for event in graph.stream(initial_state, config=config):
                if 'agent' in event:
                    # Agent is thinking or has a response
                    agent_msg = event['agent']['messages'][-1]
                    
                    # Check if agent is calling tools
                    if hasattr(agent_msg, 'tool_calls') and agent_msg.tool_calls:
                        for tool_call in agent_msg.tool_calls:
                            tool_name = tool_call.get('name', 'unknown')
                            friendly_name = tool_names.get(tool_name, f"Using {tool_name}")
                            
                            # Send tool_start event
                            yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name, 'message': friendly_name})}\n\n"
                            await asyncio.sleep(0.05)
                    
                    # Check if this is the final response
                    if hasattr(agent_msg, 'content') and agent_msg.content:
                        # Extract text from Gemini's response format
                        content = agent_msg.content
                        if isinstance(content, list):
                            # Gemini returns list of content objects
                            final_response = ""
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    final_response += item['text']
                                elif isinstance(item, str):
                                    final_response += item
                        elif isinstance(content, str):
                            final_response = content
                        else:
                            final_response = str(content)
                
                elif 'tools' in event:
                    # Tool execution completed
                    yield f"data: {json.dumps({'type': 'tool_end', 'message': 'Completed'})}\n\n"
                    await asyncio.sleep(0.05)
            
            # Send final response
            if final_response:
                yield f"data: {json.dumps({'type': 'complete', 'response': final_response, 'session_id': session_id})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No response generated'})}\n\n"
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_ready": graph is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
