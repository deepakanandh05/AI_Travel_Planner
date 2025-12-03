"""
Structured Logging Module

Production-grade JSON logging for monitoring, debugging, and audit trails.
WHY: Structured logs enable easy parsing, querying, and integration with monitoring tools.
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format.
    WHY: JSON logs are machine-readable and easily indexable by log aggregators.
    """
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Add extra fields if they exist
        # WHY: Allows us to include context like query, tools_used, latency, etc.
        if hasattr(record, 'query'):
            log_data['query'] = record.query
        if hasattr(record, 'tools_used'):
            log_data['tools_used'] = record.tools_used
        if hasattr(record, 'errors'):
            log_data['errors'] = record.errors
        if hasattr(record, 'latency_ms'):
            log_data['latency_ms'] = record.latency_ms
        if hasattr(record, 'success'):
            log_data['success'] = record.success
            
        return json.dumps(log_data)


def setup_logger(name: str = "travel_planner", log_dir: str = "logs") -> logging.Logger:
    """
    Setup structured logger with file and console handlers.
    
    WHY: Separating console (INFO) and file (DEBUG) logs allows detailed
    debugging without overwhelming terminal output.
    
    Args:
        name: Logger name
        log_dir: Directory for log files (auto-created)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    # WHY: Automatic directory creation makes deployment easier
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # File handler - JSON format, DEBUG level
    # WHY: File gets detailed logs for debugging and audit
    file_handler = logging.FileHandler(log_path / "agent.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())
    
    # Console handler - Plain format, INFO level  
    # WHY: Console gets readable logs for monitoring, not too verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
