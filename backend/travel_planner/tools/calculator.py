from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.
    Useful for summing up costs or calculating budgets.
    Input should be a valid mathematical expression string (e.g., "200 + 500 + 300").
    """
    try:
        # Use eval with restricted globals/locals for safety, though simple arithmetic is the goal
        allowed_names = {"sum": sum, "min": min, "max": max}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error calculating: {e}"
