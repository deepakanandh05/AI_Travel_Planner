from travel_planner.agent.agent_workflow import GraphBuilder
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def main():
    # Check for API keys
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY not found in environment variables. Please check your .env file.")
    
    try:
        graph_builder = GraphBuilder(model_provider="groq")
        graph = graph_builder()
        
        print("Agent initialized. Type 'quit' to exit.")
        
        messages = []
        
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "exit"]:
                break
            
            messages.append(("user", user_input))
            initial_state = {"messages": messages}
            
            # Stream the output to see steps
            print("\nAgent processing...")
            result = graph.invoke(initial_state)
            
            # Print the final response
            last_message = result['messages'][-1]
            print(f"\nAgent: {last_message.content}")
            
            # Update history with the agent's response
            messages = result['messages']
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
