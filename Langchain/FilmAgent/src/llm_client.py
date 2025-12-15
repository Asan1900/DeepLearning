"""Abstract base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMClient(ABC):
    """Base interface for LLM providers."""
    
    @abstractmethod
    def initialize_chat(self, tools: List[Dict[str, Any]], system_instruction: str = ""):
        """Initialize chat session with tools and system instruction."""
        pass
    
    @abstractmethod
    def send_message(self, message: str, context: str = "") -> Any:
        """Send a message to the model."""
        pass
    
    @abstractmethod
    def send_function_response(self, function_responses: List[Dict[str, Any]]) -> Any:
        """Send function execution results back to the model."""
        pass
    
    @abstractmethod
    def extract_function_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from the model response."""
        pass
    
    @abstractmethod
    def get_text_response(self, response: Any) -> Optional[str]:
        """Extract text content from the model response."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model and provider."""
        pass
    
    @abstractmethod
    def set_history(self, messages: List[Dict[str, str]]):
        """Set the conversation history for the client."""
        pass
