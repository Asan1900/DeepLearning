"""Logging middleware for the agent."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from ..config import LOG_FILE, LOG_LEVEL


class AgentLogger:
    """Structured logging for agent operations."""
    
    def __init__(self, log_file: Path = LOG_FILE):
        self.log_file = log_file
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure the logger."""
        self.logger = logging.getLogger("FilmAgent")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_user_query(self, user_id: int, query: str):
        """Log a user query."""
        self.logger.info(f"User {user_id} query: {query}")
        self._log_structured({
            "event": "user_query",
            "user_id": user_id,
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_tool_call(self, tool_name: str, parameters: Dict[str, Any], 
                     result: Optional[Dict[str, Any]] = None):
        """Log a tool call."""
        log_data = {
            "event": "tool_call",
            "tool_name": tool_name,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        if result:
            log_data["result_summary"] = {
                "success": result.get("success"),
                "count": result.get("count", 0)
            }
        
        self.logger.info(f"Tool call: {tool_name} with params {parameters}")
        self._log_structured(log_data)
    
    def log_agent_response(self, user_id: int, response: str):
        """Log agent response."""
        self.logger.info(f"Agent response to user {user_id}: {response[:100]}...")
        self._log_structured({
            "event": "agent_response",
            "user_id": user_id,
            "response_preview": response[:200],
            "timestamp": datetime.now().isoformat()
        })
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """Log an error."""
        log_data = {
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        if context:
            log_data["context"] = context
        
        self.logger.error(f"{error_type}: {error_message}")
        self._log_structured(log_data)
    
    def log_memory_operation(self, operation: str, details: Dict[str, Any]):
        """Log memory operations."""
        self.logger.debug(f"Memory operation: {operation}")
        self._log_structured({
            "event": "memory_operation",
            "operation": operation,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def _log_structured(self, data: Dict[str, Any]):
        """Write structured JSON log entry."""
        json_log_file = self.log_file.parent / "agent_structured.jsonl"
        with open(json_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
