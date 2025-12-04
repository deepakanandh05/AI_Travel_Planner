from langchain_core.tools import tool

@tool
def format_response(content: str) -> str:
    """
    Format travel information in a beautiful, engaging way with emojis and markdown.
    Use this tool to make your final response interesting and visually appealing.
    
    Input: Plain text content
    Output: Formatted markdown with emojis
    
    WHY: Makes responses engaging and fun to read
    """
    # This is a pass-through tool that signals the LLM to format nicely
    # The actual formatting happens in the LLM's response
    return f"✨ Formatted content ready:\n{content}"
