from langchain_core.tools import tool

@tool
def finalize_plan(plan_content: str):
    """
    Use this tool to submit the final comprehensive travel plan.
    The input should be the full, formatted travel itinerary in Markdown.
    This signals that the planning process is complete.
    """
    return "Plan submitted successfully."
