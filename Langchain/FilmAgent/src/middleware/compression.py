"""Context compression middleware."""

from typing import List
from ..memory.short_term import Message, ShortTermMemory
from ..config import COMPRESSION_THRESHOLD, MAX_CONTEXT_TOKENS


class ContextCompressor:
    """Manages context compression to stay within token limits."""
    
    def __init__(self, short_term_memory: ShortTermMemory):
        self.memory = short_term_memory
    
    def should_compress(self) -> bool:
        """Check if compression is needed."""
        estimated_tokens = self.memory.count_tokens_estimate()
        return estimated_tokens > COMPRESSION_THRESHOLD
    
    def compress_if_needed(self, user_context: str = "") -> str:
        """Compress context if needed, return summary."""
        if not self.should_compress():
            return ""
        
        # Get messages to compress (keep recent ones)
        messages = self.memory.messages
        if len(messages) <= 10:
            return ""  # Don't compress if we have few messages
        
        # Keep the last 10 messages, summarize the rest
        messages_to_summarize = messages[:-10]
        recent_messages = messages[-10:]
        
        # Create a summary
        summary = self._create_summary(messages_to_summarize, user_context)
        
        # Replace old messages with summary
        summary_message = Message(
            role="model",
            content=f"[Previous conversation summary: {summary}]"
        )
        
        self.memory.messages = [summary_message] + recent_messages
        
        return summary
    
    def _create_summary(self, messages: List[Message], user_context: str) -> str:
        """Create a summary of messages."""
        # Extract key information
        user_queries = []
        tool_calls = []
        
        for msg in messages:
            if msg.role == "user":
                user_queries.append(msg.content)
            elif msg.role == "function" and msg.tool_name:
                tool_calls.append(msg.tool_name)
        
        summary_parts = []
        
        if user_context:
            summary_parts.append(f"User info: {user_context}")
        
        if user_queries:
            summary_parts.append(
                f"User asked about: {', '.join(set(user_queries[:5]))}"
            )
        
        if tool_calls:
            tool_summary = ', '.join(set(tool_calls))
            summary_parts.append(f"Tools used: {tool_summary}")
        
        return ". ".join(summary_parts) if summary_parts else "General film discussion"
