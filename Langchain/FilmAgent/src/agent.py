"""Main agent orchestration."""

from typing import Optional, Dict, Any
import re

from .gemini_client import GeminiClient
from .ollama_client import OllamaClient
from .config import LLM_PROVIDER
from .data.films_db import FilmsDatabase
from .tools.film_tools import create_film_tools
from .memory.short_term import ShortTermMemory
from .memory.long_term import LongTermMemory
from .middleware.logger import AgentLogger
from .middleware.compression import ContextCompressor
from .middleware.orchestrator import ToolOrchestrator


class FilmAgent:
    """Intelligent film agent with memory and multi-tool calling."""
    
    def __init__(self):
        # Initialize components
        self.films_db = FilmsDatabase()
        
        # Initialize LLM Client based on provider
        if LLM_PROVIDER == "ollama":
            self.llm_client = OllamaClient()
        else:
            self.llm_client = GeminiClient()
            
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.logger = AgentLogger()
        
        # Initialize tools
        self.tools = create_film_tools(self.films_db)
        self.orchestrator = ToolOrchestrator(self.tools, self.logger)
        
        # Initialize compressor
        self.compressor = ContextCompressor(self.short_term_memory)
        
        # User session
        self.user_id: Optional[int] = None
        
        # Initialize LLM chat with tools
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client with tools and system instruction."""
        system_instruction = """You are an intelligent film assistant. You help users discover and learn about films.

You have access to tools to search for films by:
- Title (partial matches supported)
- Genre
- Rating range
- Actor name

You can call multiple tools in sequence to answer complex queries. For example:
- "Show me action movies with high ratings" → filter_by_genre + search_by_rating
- "Find sci-fi films starring Tom Hanks" → filter_by_genre + search_by_actor

Always be helpful, conversational, and personalize responses based on user preferences when available.
When presenting film results, highlight the most relevant information and make recommendations."""
        
        tool_declarations = self.orchestrator.get_tool_declarations()
        self.llm_client.initialize_chat(tool_declarations, system_instruction)
    
    def switch_provider(self, provider: str, model_name: Optional[str] = None) -> str:
        """Switch the LLM provider at runtime."""
        provider = provider.lower()
        
        # 1. Capture current history
        current_history = self.short_term_memory.get_generic_history()
        
        # 2. Initialize new client
        try:
            if provider == "ollama":
                new_client = OllamaClient()
                if model_name:
                    new_client.model = model_name
            elif provider == "gemini":
                new_client = GeminiClient()
                if model_name:
                    new_client.model_name = model_name
            else:
                return f"Unknown provider: {provider}"
            
            # 3. Initialize chat with tools (system instruction repeated)
            # Extract system instruction from existing client?
            # Or just use the standard one defined in _initialize_llm
            # We'll reuse the standard init logic but pointing to new client
            
            old_client = self.llm_client
            self.llm_client = new_client
            try:
                self._initialize_llm()
            except Exception as e:
                # Rollback
                self.llm_client = old_client
                return f"Failed to initialize {provider}: {e}"
            
            # 4. Hydrate history
            self.llm_client.set_history(current_history)
            
            return f"Successfully switched to {provider} ({self.llm_client.get_model_info()['model']})"
            
        except Exception as e:
            return f"Error switching provider: {e}"

    def start_session(self, user_name: Optional[str] = None) -> str:
        """Start a new user session."""
        self.user_id = self.long_term_memory.get_or_create_user(user_name)
        
        if user_name:
            self.long_term_memory.set_user_name(self.user_id, user_name)
            welcome_msg = f"Hello {user_name}! I'm your film assistant. How can I help you discover great films today?"
        else:
            welcome_msg = "Hello! I'm your film assistant. How can I help you discover great films today?"
        
        self.logger.log_memory_operation("session_start", {"user_id": self.user_id, "user_name": user_name})
        return welcome_msg
    
    def process_query(self, query: str) -> str:
        """Process a user query and return response."""
        if not self.user_id:
            self.start_session()
        
        # Log query
        self.logger.log_user_query(self.user_id, query)
        
        # Extract user name if mentioned
        self._extract_user_info(query)
        
        # Add to short-term memory
        self.short_term_memory.add_user_message(query)
        
        # Check if compression needed
        self.compressor.compress_if_needed(
            self.long_term_memory.get_user_context(self.user_id)
        )
        
        # Build context
        context = self._build_context()
        
        # Send to Gemini
        try:
            response = self.llm_client.send_message(query, context)
            
            # Check for function calls
            function_calls = self.llm_client.extract_function_calls(response)
            
            if function_calls:
                # Execute tools
                final_response = self._handle_function_calls(function_calls)
            else:
                # Direct text response
                final_response = self.llm_client.get_text_response(response) or "I'm not sure how to help with that."
            
            # Add to memory
            self.short_term_memory.add_assistant_message(final_response)
            self.long_term_memory.save_conversation_turn(self.user_id, "assistant", final_response)
            
            # Extract and save preferences
            self._extract_preferences(query, final_response)
            
            # Log response
            self.logger.log_agent_response(self.user_id, final_response)
            
            return final_response
            
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            self.logger.log_error("query_processing_error", str(e), {"query": query})
            return error_msg
    
    def _handle_function_calls(self, function_calls: list) -> str:
        """Handle function calls from LLM."""
        # Execute all tools
        results = self.orchestrator.execute_multiple_tools(function_calls)
        
        # Format results for LLM
        formatted_results = self.orchestrator.format_tool_results_for_llm(results)
        
        # Log tool calls
        for result in results:
            self.short_term_memory.add_tool_call(
                result["tool_name"],
                str(result["result"])
            )
        
        # Send results back to Gemini
        function_responses = [
            {
                "name": result["tool_name"],
                "response": result["result"]
            }
            for result in results
        ]
        
        response = self.llm_client.send_function_response(function_responses)
        final_text = self.llm_client.get_text_response(response)
        
        return final_text or formatted_results
    
    def _build_context(self) -> str:
        """Build context string for the LLM."""
        context_parts = []
        
        # User context from long-term memory
        user_context = self.long_term_memory.get_user_context(self.user_id)
        if user_context:
            context_parts.append(f"=== User Profile ===\n{user_context}")
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def _extract_user_info(self, query: str):
        """Extract user information from query."""
        # Check for name introduction
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query.lower())
            if match:
                name = match.group(1).capitalize()
                self.long_term_memory.set_user_name(self.user_id, name)
                self.logger.log_memory_operation("user_name_extracted", {"name": name})
                break
    
    def _extract_preferences(self, query: str, response: str):
        """Extract and save user preferences from conversation."""
        query_lower = query.lower()
        
        # Extract genre preferences
        genre_keywords = {
            "sci-fi": ["sci-fi", "science fiction", "scifi"],
            "action": ["action"],
            "drama": ["drama"],
            "comedy": ["comedy", "funny"],
            "thriller": ["thriller", "suspense"],
            "horror": ["horror", "scary"],
            "romance": ["romance", "romantic"],
            "animation": ["animation", "animated"]
        }
        
        for genre, keywords in genre_keywords.items():
            for keyword in keywords:
                if keyword in query_lower and ("love" in query_lower or "like" in query_lower or "favorite" in query_lower):
                    self.long_term_memory.add_preference(
                        self.user_id,
                        "favorite_genre",
                        genre,
                        confidence=0.8
                    )
                    self.logger.log_memory_operation(
                        "preference_extracted",
                        {"type": "genre", "value": genre}
                    )
        
        # Extract rating preferences
        if "high rating" in query_lower or "best" in query_lower or "top rated" in query_lower:
            self.long_term_memory.add_preference(
                self.user_id,
                "rating_preference",
                "high_rating",
                confidence=0.7
            )
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        return self.short_term_memory.get_context_summary()
    
    @property
    def agent_info(self) -> Dict[str, str]:
        """Get information about the agent's LLM configuration."""
        return self.llm_client.get_model_info()
