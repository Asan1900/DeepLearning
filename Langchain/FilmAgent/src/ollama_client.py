"""Ollama (local) client wrapper."""

import os
from typing import List, Dict, Any, Optional
import ollama

from .config import OLLAMA_BASE_URL, OLLAMA_MODEL
from .llm_client import LLMClient


class OllamaClient(LLMClient):
    """Wrapper for Ollama API with function calling support."""
    
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.client = ollama.Client(host=self.base_url)
        self.messages: List[Dict[str, Any]] = []
        self.tools: List[Dict[str, Any]] = []
    
    def initialize_chat(self, tools: List[Dict[str, Any]], system_instruction: str = ""):
        """Initialize a chat session."""
        self.messages = []
        
        # Add system instruction if provided
        if system_instruction:
            self.messages.append({
                "role": "system",
                "content": system_instruction
            })
        
        # Store tools standard format
        # Ollama supports tools in a format very similar to OpenAI/Gemini
        self.tools = []
        for tool in tools:
            # Adapt tool to Ollama format signature
            self.tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
    
    def send_message(self, message: str, context: str = "") -> Any:
        """Send a message and get response."""
        # Add context if provided
        full_message = f"{context}\n\n{message}" if context else message
        
        self.messages.append({
            "role": "user",
            "content": full_message
        })
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tools
            )
        except ollama.ResponseError as e:
            if e.status_code == 400 and "does not support tools" in str(e):
                # Fallback: model doesn't support tools, run without them
                response = self.client.chat(
                    model=self.model,
                    messages=self.messages
                )
            else:
                raise e
        
        # Store response in history
        self.messages.append(response['message'])
        
        return response
    
    def send_function_response(self, function_responses: List[Dict[str, Any]]) -> Any:
        """Send function call results back to the model."""
        # Add tool outputs to history
        for func_res in function_responses:
            # We must find the corresponding tool call ID if possible, but Ollama simplified doesn't always strictly use IDs in the simplified API, check response structure.
            # But standard OpenAI-like tool usage requires 'tool_call_id'.
            # Ollama's python lib handles message objects.
            # We just mock a tool response message.
            
            # Note: Ollama expects the role 'tool' for tool outputs.
            self.messages.append({
                "role": "tool",
                "content": str(func_res["response"]),
                # "name": func_res["name"] # some implementations use name
            })

        # Get follow-up response
        # Get follow-up response
        try:
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tools
            )
        except ollama.ResponseError as e:
            if e.status_code == 400 and "does not support tools" in str(e):
                 # Fallback
                response = self.client.chat(
                    model=self.model,
                    messages=self.messages
                )
            else:
                raise e
        
        self.messages.append(response['message'])
        return response
    
    def extract_function_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract function calls from model response."""
        message = response['message']
        if 'tool_calls' in message and message['tool_calls']:
            return [
                {
                    "name": tool_call['function']['name'],
                    "args": tool_call['function']['arguments']
                }
                for tool_call in message['tool_calls']
            ]
        return []
    
    def get_text_response(self, response: Any) -> Optional[str]:
        """Extract text from model response."""
        message = response['message']
        return message.get('content')
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model and provider."""
        return {
            "provider": "Ollama (Local)",
            "model": self.model
        }
    
    def set_history(self, messages: List[Dict[str, str]]):
        """Set the conversation history for the client."""
        # Preserve system message if it exists
        system_msg = None
        if self.messages and self.messages[0]["role"] == "system":
            system_msg = self.messages[0]
        
        new_history = []
        if system_msg:
            new_history.append(system_msg)
            
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # Ollama uses 'assistant' and 'tool' already
            # Just ensure keys match what we expect
            new_history.append({
                "role": role,
                "content": content
            })
            
        self.messages = new_history
