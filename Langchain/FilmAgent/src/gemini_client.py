"""Gemini API client wrapper."""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json

from .config import GEMINI_API_KEY, GEMINI_MODEL, validate_config
from .llm_client import LLMClient


class GeminiClient(LLMClient):
    """Wrapper for Google Gemini API with function calling support."""
    
    def __init__(self):
        validate_config()
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL
        self.model = None
        self.chat = None
    
    def initialize_chat(self, tools: List[Dict[str, Any]], system_instruction: str = ""):
        """Initialize a chat session with function calling tools."""
        # Convert tool declarations to Gemini format
        gemini_tools = self._convert_tools_to_gemini_format(tools)
        
        # Create model with tools
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            tools=gemini_tools if gemini_tools else None,
            system_instruction=system_instruction
        )
        
        # Start chat
        self.chat = self.model.start_chat(history=[])
    
    def send_message(self, message: str, context: str = "") -> Any:
        """Send a message and get response."""
        if not self.chat:
            raise RuntimeError("Chat not initialized. Call initialize_chat first.")
        
        # Prepend context if provided
        full_message = f"{context}\n\n{message}" if context else message
        
        response = self.chat.send_message(full_message)
        return response
    
    def send_function_response(self, function_responses: List[Dict[str, Any]]) -> Any:
        """Send function call results back to the model."""
        if not self.chat:
            raise RuntimeError("Chat not initialized. Call initialize_chat first.")
        
        # Format function responses for Gemini
        parts = []
        for func_response in function_responses:
            parts.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=func_response["name"],
                        response={"result": func_response["response"]}
                    )
                )
            )
        
        response = self.chat.send_message(parts)
        return response
    
    def _convert_tools_to_gemini_format(self, tools: List[Dict[str, Any]]) -> List[Any]:
        """Convert tool declarations to Gemini function declarations."""
        if not tools:
            return []
        
        gemini_functions = []
        for tool in tools:
            # Create function declaration
            func_decl = genai.protos.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        param_name: genai.protos.Schema(
                            type=self._get_gemini_type(param_schema.get("type", "string")),
                            description=param_schema.get("description", "")
                        )
                        for param_name, param_schema in tool["parameters"]["properties"].items()
                    },
                    required=tool["parameters"].get("required", [])
                )
            )
            gemini_functions.append(func_decl)
        
        return [genai.protos.Tool(function_declarations=gemini_functions)]
    
    def _get_gemini_type(self, json_type: str) -> genai.protos.Type:
        """Convert JSON schema type to Gemini type."""
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT
        }
        return type_mapping.get(json_type, genai.protos.Type.STRING)
    
    def extract_function_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract function calls from model response."""
        function_calls = []
        
        for part in response.parts:
            if hasattr(part, 'function_call') and part.function_call:
                fc = part.function_call
                function_calls.append({
                    "name": fc.name,
                    "args": dict(fc.args)
                })
        
        return function_calls
    
    def get_text_response(self, response: Any) -> Optional[str]:
        """Extract text from model response."""
        try:
            for part in response.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text
            pass
        except Exception:
            pass
        return None
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model and provider."""
        return {
            "provider": "Google Gemini",
            "model": self.model_name
        }
    
    def set_history(self, messages: List[Dict[str, str]]):
        """Set the conversation history for the client."""
        gemini_history = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # Map generic roles to Gemini roles
            if role == "assistant":
                role = "model"
            elif role == "tool":
                role = "function" # Gemini uses function role for returns
            
            # Create generic part
            # Note: For strict reconstruction we might need more details (tool calls vs text)
            # But for simple text history hydration:
            gemini_history.append({
                "role": role,
                "parts": [{"text": content}]
            })
            
        # Re-initialize chat with history
        if self.model:
            self.chat = self.model.start_chat(history=gemini_history)
