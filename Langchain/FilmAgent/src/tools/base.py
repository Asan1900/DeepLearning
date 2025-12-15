"""Base tool interface for the agent."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Tool(ABC):
    """Base class for all agent tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for function calling."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the LLM."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Tool parameters schema (JSON Schema format)."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    def to_gemini_function(self) -> Dict[str, Any]:
        """Convert tool to Gemini function declaration format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": self._get_required_params()
            }
        }
    
    def _get_required_params(self) -> List[str]:
        """Extract required parameters from schema."""
        return [
            param_name 
            for param_name, param_schema in self.parameters.items()
            if param_schema.get("required", False)
        ]
