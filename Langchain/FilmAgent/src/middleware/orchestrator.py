"""Tool orchestration middleware."""

import json
from typing import Dict, Any, List, Optional
from ..tools.base import Tool


class ToolOrchestrator:
    """Manages tool execution and result combination."""
    
    def __init__(self, tools: List[Tool], logger=None):
        self.tools = {tool.name: tool for tool in tools}
        self.logger = logger
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool with error handling."""
        if tool_name not in self.tools:
            error_msg = f"Unknown tool: {tool_name}"
            if self.logger:
                self.logger.log_error("tool_not_found", error_msg, {"tool_name": tool_name})
            return {
                "success": False,
                "error": error_msg
            }
        
        tool = self.tools[tool_name]
        
        try:
            # Log tool call
            if self.logger:
                self.logger.log_tool_call(tool_name, parameters)
            
            # Execute tool
            result = tool.execute(**parameters)
            
            # Log result
            if self.logger:
                self.logger.log_tool_call(tool_name, parameters, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    "tool_execution_error",
                    error_msg,
                    {"tool_name": tool_name, "parameters": parameters}
                )
            return {
                "success": False,
                "error": error_msg
            }
    
    def execute_multiple_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple tools in sequence."""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            parameters = tool_call.get("args", {})
            
            result = self.execute_tool(tool_name, parameters)
            results.append({
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            })
        
        return results
    
    def format_tool_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """Format tool results for LLM consumption."""
        if not results:
            return "No tool results available."
        
        formatted_parts = []
        
        for result_data in results:
            tool_name = result_data["tool_name"]
            result = result_data["result"]
            
            if not result.get("success", False):
                formatted_parts.append(
                    f"Tool '{tool_name}' failed: {result.get('error', 'Unknown error')}"
                )
                continue
            
            # Format successful results
            if tool_name == "search_by_title":
                formatted_parts.append(self._format_film_results(result, "title search"))
            elif tool_name == "filter_by_genre":
                formatted_parts.append(self._format_film_results(result, f"genre '{result.get('genre')}'"))
            elif tool_name == "search_by_rating":
                formatted_parts.append(self._format_film_results(result, f"rating {result.get('rating_range')}"))
            elif tool_name == "search_by_actor":
                formatted_parts.append(self._format_film_results(result, f"actor '{result.get('actor')}'"))
            else:
                formatted_parts.append(f"Tool '{tool_name}' returned: {json.dumps(result, indent=2)}")
        
        return "\n\n".join(formatted_parts)
    
    def _format_film_results(self, result: Dict[str, Any], search_type: str) -> str:
        """Format film search results."""
        films = result.get("films", [])
        count = result.get("count", 0)
        
        if count == 0:
            return f"No films found for {search_type}."
        
        lines = [f"Found {count} film(s) for {search_type}:"]
        
        for i, film in enumerate(films[:10], 1):  # Limit to top 10
            title = film.get("title", "Unknown")
            year = film.get("year", "N/A")
            rating = film.get("rating", "N/A")
            genres = ", ".join(film.get("genres", []))
            actors = ", ".join(film.get("actors", [])[:3])  # Top 3 actors
            
            lines.append(
                f"{i}. {title} ({year}) - Rating: {rating}/10\n"
                f"   Genres: {genres}\n"
                f"   Starring: {actors}"
            )
        
        return "\n".join(lines)
    
    def get_tool_declarations(self) -> List[Dict[str, Any]]:
        """Get tool declarations for Gemini function calling."""
        return [tool.to_gemini_function() for tool in self.tools.values()]
