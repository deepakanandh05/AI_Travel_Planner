from langchain_core.tools import tool

@tool
def validate_budget(total_cost: float, budget_limit: float) -> str:
    """
    Validate if the total cost is within the budget limit.
    
    Args:
        total_cost: The total calculated cost of the plan
        budget_limit: The user's maximum budget
    
    Returns:
        Validation result with instructions
        
    WHY: Ensures agent stays within budget and iterates if needed
    """
    if total_cost <= budget_limit:
        savings = budget_limit - total_cost
        return f"✅ BUDGET VALID: Total ₹{total_cost} is within budget of ₹{budget_limit}. Savings: ₹{savings}. You may present this plan to the user."
    else:
        overage = total_cost - budget_limit
        return f"❌ BUDGET EXCEEDED: Total ₹{total_cost} exceeds budget of ₹{budget_limit} by ₹{overage}. You MUST adjust the plan by: 1) Choosing cheaper hotels, 2) Reducing paid activities, 3) Selecting budget restaurants. Recalculate and validate again. DO NOT present this plan to the user."
