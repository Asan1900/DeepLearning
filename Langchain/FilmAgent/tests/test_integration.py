"""Integration tests for the Film Agent."""

import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.agent import FilmAgent
from src.data.films_db import FilmsDatabase
from src.data.seed_data import seed_films_database
from src.config import DATA_DIR

# Use a test database directory
TEST_DATA_DIR = Path("test_data")
TEST_FILMS_DB = TEST_DATA_DIR / "films.db"
TEST_MEMORY_DB = TEST_DATA_DIR / "memory.db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment."""
    # Create test directory
    TEST_DATA_DIR.mkdir(exist_ok=True)
    
    # Patch config paths
    with patch("src.config.FILMS_DB_PATH", TEST_FILMS_DB), \
         patch("src.config.MEMORY_DB_PATH", TEST_MEMORY_DB), \
         patch("src.data.films_db.FILMS_DB_PATH", TEST_FILMS_DB), \
         patch("src.memory.long_term.MEMORY_DB_PATH", TEST_MEMORY_DB):
        
        # Seed database
        db = FilmsDatabase(TEST_FILMS_DB)
        # Use existing seed function but redirect db path via patch
        seed_films_database()
        
        yield
        
    # Cleanup
    shutil.rmtree(TEST_DATA_DIR)


@pytest.fixture
def agent():
    """Create an agent instance with mocked Gemini."""
    with patch("src.config.FILMS_DB_PATH", TEST_FILMS_DB), \
         patch("src.config.MEMORY_DB_PATH", TEST_MEMORY_DB), \
         patch("src.data.films_db.FILMS_DB_PATH", TEST_FILMS_DB), \
         patch("src.memory.long_term.MEMORY_DB_PATH", TEST_MEMORY_DB):
        
        # Mock Gemini client to avoid actual API calls during automated tests
        with patch("src.agent.GeminiClient") as MockGemini:
            mock_client = MockGemini.return_value
            
            # Setup default mockup responses
            mock_client.send_message.return_value = MagicMock()
            mock_client.extract_function_calls.return_value = []
            mock_client.get_text_response.return_value = "Mock response"
            
            agent = FilmAgent()
            agent.start_session("TestUser")
            return agent


def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.user_id is not None
    assert agent.films_db is not None
    assert agent.tools is not None
    assert len(agent.tools) == 4


def test_tool_execution(agent):
    """Test direct tool execution via orchestrator."""
    # Test title search
    result = agent.orchestrator.execute_tool(
        "search_by_title", 
        {"title": "Inception"}
    )
    assert result["success"] is True
    assert result["count"] > 0
    assert result["films"][0]["title"] == "Inception"

    # Test genre filter
    result = agent.orchestrator.execute_tool(
        "filter_by_genre", 
        {"genre": "Sci-Fi"}
    )
    assert result["success"] is True
    assert result["count"] > 0
    assert any(f["title"] == "Inception" for f in result["films"])


def test_memory_persistence(agent):
    """Test that preferences are saved."""
    # Simulate extraction of preference
    agent.long_term_memory.add_preference(
        agent.user_id, "favorite_genre", "Sci-Fi"
    )
    
    # Retrieve preferences
    prefs = agent.long_term_memory.get_preferences(agent.user_id)
    assert len(prefs) > 0
    assert prefs[0]["preference_value"] == "Sci-Fi"


def test_context_building(agent):
    """Test context construction."""
    # Add some context
    agent.long_term_memory.add_preference(
        agent.user_id, "favorite_genre", "Action"
    )
    
    context = agent._build_context()
    assert "User Profile" in context
    assert "Action" in context


def test_compression_logic(agent):
    """Test compression logic trigger."""
    # Patch the threshold to be very low for testing
    with patch("src.middleware.compression.COMPRESSION_THRESHOLD", 10):
        # Add messages
        for i in range(20):
            agent.short_term_memory.add_user_message(f"Long message content to ensure we exceed threshold {i}")
        
        assert agent.compressor.should_compress() is True
        
        # Test compression execution
        summary = agent.compressor.compress_if_needed("User context")
        assert isinstance(summary, str)
        assert len(agent.short_term_memory.messages) < 20  # Messages should be compressed


def test_full_flow_logic(agent):
    """Test the full query processing logic (with mocked LLM)."""
    # 1. Normal text query
    agent.llm_client.extract_function_calls.return_value = []
    agent.llm_client.get_text_response.return_value = "Hello there"
    
    response = agent.process_query("Hi")
    assert response == "Hello there"
    
    # 2. Query triggering tool
    # Mock LLM returning a function call
    agent.llm_client.extract_function_calls.side_effect = [
        [{"name": "search_by_title", "args": {"title": "Matrix"}}], # First call returns tool
        [] # Second call (after tool result) returns text
    ]
    
    # Mock LLM response after tool execution
    agent.llm_client.get_text_response.side_effect = [
        None, # First response has no text, only function call
        "I found The Matrix for you." # Final response
    ]
    
    response = agent.process_query("Find Matrix")
    
    # Check if tool was executed (trace via log or side effect)
    # Since we use real DB, we can check if it didn't crash and returned string
    assert "Matrix" in response or "found" in response
