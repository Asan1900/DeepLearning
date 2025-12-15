"""Tests for Ollama client."""

import pytest
from unittest.mock import MagicMock, patch
from src.ollama_client import OllamaClient


@pytest.fixture
def ollama_client():
    with patch("ollama.Client") as MockClient:
        client = OllamaClient()
        client.client = MockClient.return_value
        return client


def test_initialization(ollama_client):
    tools = [
        {
            "name": "search_movie",
            "description": "Find a movie",
            "parameters": {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"]
            }
        }
    ]
    ollama_client.initialize_chat(tools, "You are a helpful assistant")
    
    assert len(ollama_client.messages) == 1
    assert ollama_client.messages[0]["role"] == "system"
    assert len(ollama_client.tools) == 1
    assert ollama_client.tools[0]["function"]["name"] == "search_movie"


def test_send_message(ollama_client):
    # Mock response
    mock_response = {
        "message": {
            "role": "assistant",
            "content": "Hello!"
        }
    }
    ollama_client.client.chat.return_value = mock_response
    
    response = ollama_client.send_message("Hi")
    
    # Check if message was added to history
    assert len(ollama_client.messages) == 2  # user + assistant
    assert ollama_client.messages[-2]["role"] == "user"
    assert ollama_client.messages[-1]["role"] == "assistant"
    
    # Check return value
    assert ollama_client.get_text_response(response) == "Hello!"


def test_tool_call_handling(ollama_client):
    # Mock response with tool call
    mock_response = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "search_movie",
                        "arguments": {"title": "Inception"}
                    }
                }
            ]
        }
    }
    ollama_client.client.chat.return_value = mock_response
    
    response = ollama_client.send_message("Find Inception")
    
    calls = ollama_client.extract_function_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "search_movie"
    assert calls[0]["args"]["title"] == "Inception"
