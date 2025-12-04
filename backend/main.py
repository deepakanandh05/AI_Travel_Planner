from travel_planner.agent.agent_workflow import GraphBuilder
from travel_planner.core.validators import validate_user_input, validate_agent_output
from travel_planner.utils.logger import setup_logger
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Setup production logger
logger = setup_logger()

def main():
    try:
        logger.info("Initializing AI Travel Planner Agent")
        graph_builder = GraphBuilder(model_provider="gemini")
        graph = graph_builder()
        
        print("=" * 60)
        print("AI Travel Planner - Production Ready")
        print("Type 'quit' to exit")
        print("=" * 60)
        
        messages = []
        
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "exit"]:
                logger.info("User exited application")
                break
            
            # FEATURE 1: Input Validation
            # WHY: Prevents prompt injection and ensures data quality
            validation_result = validate_user_input(user_input)
            if not validation_result["valid"]:
                error_msg = validation_result["error_message"]
                logger.warning(
                    "Invalid user input",
                    extra={
                        "query": user_input[:100],  # Log first 100 chars
                        "error": error_msg,
                        "success": False
                    }
                )
                print(f"\n❌ {error_msg}")
                continue
            
            # Start timing for latency tracking
            start_time = time.time()
            tools_used = []
            errors = []
            
            try:
                messages.append(("user", user_input))
                initial_state = {"messages": messages}
                
                print("\n🤖 Agent processing...")
                logger.info("Processing user query", extra={"query": user_input})
                
                # Invoke the agent
                result = graph.invoke(initial_state)
                
                # Extract response
                last_message = result['messages'][-1]
                response_content = last_message.content
                
                # Track which tools were used (if available)
                # WHY: Helps debug and monitor which tools are being called
                for msg in result['messages']:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tools_used.extend([tc['name'] for tc in msg.tool_calls])
                
                # FEATURE 5: Output Validation
                # WHY: Ensures response quality and catches hallucination artifacts
                output_validation = validate_agent_output(response_content, user_input)
                
                if not output_validation["valid"]:
                    logger.warning(
                        "Low quality response detected",
                        extra={
                            "query": user_input[:100],
                            "issues": output_validation["issues"],
                            "score": output_validation["score"]
                        }
                    )
                    print("\n⚠️ Response quality issues detected:")
                    for issue in output_validation["issues"]:
                        print(f"  - {issue}")
                
                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)
                
                # FEATURE 3: Structured Logging
                # WHY: Production monitoring and debugging
                logger.info(
                    "Successfully processed query",
                    extra={
                        "query": user_input[:100],  # First 100 chars
                        "tools_used": list(set(tools_used)),  # Unique tools
                        "latency_ms": latency_ms,
                        "success": True,
                        "output_score": output_validation["score"]
                    }
                )
                
                # Display response with quality indicator
                quality_emoji = "✅" if output_validation["score"] >= 80 else "⚠️"
                print(f"\n{quality_emoji} Agent: {response_content}")
                print(f"\n📊 Response time: {latency_ms}ms | Quality: {output_validation['score']}/100")
                
                # Update history with the agent's response
                messages = result['messages']
                
            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)
                error_msg = str(e)
                errors.append(error_msg)
                
                # FEATURE 3: Error Logging
                logger.error(
                    "Error processing query",
                    extra={
                        "query": user_input[:100],
                        "tools_used": list(set(tools_used)),
                        "errors": errors,
                        "latency_ms": latency_ms,
                        "success": False
                    }
                )
                
                print(f"\n❌ An error occurred: {error_msg}")
                print("Please try again with a different query.")
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error occurred: {e}")

if __name__ == "__main__":
    main()

