"""Short-term memory for conversation context."""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str  # 'user', 'model', 'function'
    content: str
    timestamp: datetime = None
    tool_name: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "role": self.role,
            "parts": [{"text": self.content}]
        }
        if self.tool_name:
            result["tool_name"] = self.tool_name
        return result


class ShortTermMemory:
    """Manages short-term conversation history."""
    
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages: List[Message] = []
    
    def add_user_message(self, content: str):
        """Add a user message to history."""
        self.messages.append(Message(role="user", content=content))
        self._trim_if_needed()
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to history."""
        self.messages.append(Message(role="model", content=content))
        self._trim_if_needed()
    
    def add_tool_call(self, tool_name: str, result: str):
        """Add a tool call result to history."""
        self.messages.append(
            Message(role="function", content=result, tool_name=tool_name)
        )
        self._trim_if_needed()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history in Gemini format."""
        return [msg.to_dict() for msg in self.messages]
    
    def get_generic_history(self) -> List[Dict[str, Any]]:
        """Get history in a generic format for any LLM."""
        generic_history = []
        for msg in self.messages:
            role = msg.role
            # Normalize roles
            if role == "model":
                role = "assistant"
            elif role == "function":
                role = "tool"
            
            generic_history.append({
                "role": role,
                "content": msg.content,
                "tool_name": msg.tool_name
            })
        return generic_history
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent messages."""
        return self.messages[-count:]
    
    def clear(self):
        """Clear all conversation history."""
        self.messages.clear()
    
    def _trim_if_needed(self):
        """Trim old messages if we exceed max_messages."""
        if len(self.messages) > self.max_messages:
            # Keep the most recent messages
            self.messages = self.messages[-self.max_messages:]
    
    def get_context_summary(self) -> str:
        """Generate a summary of the conversation context."""
        if not self.messages:
            return "No conversation history."
        
        summary_parts = []
        for msg in self.messages[-10:]:  # Last 10 messages
            role = msg.role
            preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary_parts.append(f"{role}: {preview}")
        
        return "\n".join(summary_parts)
    
    def count_tokens_estimate(self) -> int:
        """Rough estimate of token count in conversation history."""
        # Rough estimate: ~4 characters per token
        total_chars = sum(len(msg.content) for msg in self.messages)
        return total_chars // 4
