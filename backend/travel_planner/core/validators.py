"""
Input and Output Validation Module

Implements production-grade validation for:
- User input sanitization (prevent prompt injection)
- Agent output quality checks (prevent hallucination artifacts)
"""

import re
from typing import Dict


def validate_user_input(query: str) -> Dict[str, any]:
    """
    Validate user input before processing by the agent.
    
    WHY: Prevents prompt injection attacks and ensures data quality.
    This is critical for production systems to avoid LLM jailbreaking.
    
    Args:
        query: User's travel planning query
        
    Returns:
        {"valid": bool, "error_message": str}
    """
    # Check if query exists and is string
    if not query or not isinstance(query, str):
        return {"valid": False, "error_message": "Query must be a non-empty string"}
    
    # Strip whitespace for length check
    query = query.strip()
    
    # Check length constraints (3-2000 chars)
    # WHY: Too short = likely not meaningful, too long = potential abuse
    if len(query) < 3:
        return {"valid": False, "error_message": "Query too short (minimum 3 characters)"}
    
    if len(query) > 2000:
        return {"valid": False, "error_message": "Query too long (maximum 2000 characters)"}
    
    # Check for prompt injection patterns
    # WHY: Attackers try to override system prompts with these patterns
    injection_patterns = [
        r"ignore\s+(previous|above|all)\s+instructions",
        r"disregard\s+(previous|above|all)",
        r"forget\s+(previous|above|everything)",
        r"system\s*:\s*you\s+are",
        r"<\s*system\s*>",
        r"print\s+your\s+(instructions|prompt)",
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return {
                "valid": False, 
                "error_message": "Invalid query: contains suspicious patterns"
            }
    
    # All checks passed
    return {"valid": True, "error_message": ""}


def validate_agent_output(response: str, query: str = "") -> Dict[str, any]:
    """
    Validate agent's response before returning to user.
    
    WHY: Ensures response quality and catches LLM hallucination artifacts
    like placeholders or code snippets that shouldn't be in travel advice.
    
    Args:
        response: Agent's generated response
        query: Original user query (for context, optional)
        
    Returns:
        {"valid": bool, "issues": list, "score": int}
    """
    issues = []
    
    # Check if response exists
    if not response or not isinstance(response, str):
        return {"valid": False, "issues": ["Empty or invalid response"], "score": 0}
    
    response = response.strip()
    
    # Check minimum response length
    # WHY: Very short responses are likely errors or incomplete
    if len(response) < 10:
        issues.append("Response too short (less than 10 characters)")
    
    # Check for common placeholder patterns
    # WHY: LLMs sometimes generate templates with placeholders instead of real content
    placeholder_patterns = [
        r"\[insert\s+\w+\]",
        r"\[your\s+\w+\]",
        r"\{\{\s*\w+\s*\}\}",
        r"TODO:",
        r"PLACEHOLDER",
    ]
    
    for pattern in placeholder_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            issues.append(f"Contains placeholder pattern: {pattern}")
    
    # Check for XML/HTML tags that shouldn't be in natural language
    # WHY: Sometimes LLMs leak internal formatting or function call syntax
    if re.search(r"<(function|tool|system|assistant|user)[\s>]", response, re.IGNORECASE):
        issues.append("Contains XML/code artifacts")
    
    # Calculate quality score (0-100)
    score = 100
    score -= len(issues) * 20  # Deduct 20 points per issue
    score = max(0, min(100, score))  # Clamp to 0-100
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "score": score
    }
