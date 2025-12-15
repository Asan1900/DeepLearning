"""Film search tools for the agent."""

import json
from typing import Dict, Any
from .base import Tool
from ..data.films_db import FilmsDatabase


class SearchByTitleTool(Tool):
    """Tool for searching films by title."""
    
    def __init__(self, db: FilmsDatabase):
        self.db = db
    
    @property
    def name(self) -> str:
        return "search_by_title"
    
    @property
    def description(self) -> str:
        return "Search for films by title. Supports partial matches and is case-insensitive. Returns up to 10 matching films."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "title": {
                "type": "string",
                "description": "The film title or partial title to search for",
                "required": True
            }
        }
    
    def execute(self, title: str) -> Dict[str, Any]:
        """Execute title search."""
        results = self.db.search_by_title(title)
        return {
            "success": True,
            "count": len(results),
            "films": results
        }


class FilterByGenreTool(Tool):
    """Tool for filtering films by genre."""
    
    def __init__(self, db: FilmsDatabase):
        self.db = db
    
    @property
    def name(self) -> str:
        return "filter_by_genre"
    
    @property
    def description(self) -> str:
        available_genres = self.db.get_all_genres()
        genres_str = ", ".join(available_genres) if available_genres else "various genres"
        return f"Filter films by genre. Available genres include: {genres_str}. Returns up to 20 films."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "genre": {
                "type": "string",
                "description": "The genre to filter by (e.g., 'Sci-Fi', 'Action', 'Drama', 'Thriller')",
                "required": True
            }
        }
    
    def execute(self, genre: str) -> Dict[str, Any]:
        """Execute genre filter."""
        results = self.db.filter_by_genre(genre)
        return {
            "success": True,
            "genre": genre,
            "count": len(results),
            "films": results
        }


class SearchByRatingTool(Tool):
    """Tool for searching films by rating range."""
    
    def __init__(self, db: FilmsDatabase):
        self.db = db
    
    @property
    def name(self) -> str:
        return "search_by_rating"
    
    @property
    def description(self) -> str:
        return "Search for films within a rating range. Ratings are on a scale of 0-10. Returns up to 20 films sorted by rating."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "min_rating": {
                "type": "number",
                "description": "Minimum rating (0-10)",
                "required": True
            },
            "max_rating": {
                "type": "number",
                "description": "Maximum rating (0-10). Defaults to 10.0 if not specified.",
                "required": False
            }
        }
    
    def execute(self, min_rating: float, max_rating: float = 10.0) -> Dict[str, Any]:
        """Execute rating search."""
        results = self.db.search_by_rating(min_rating, max_rating)
        return {
            "success": True,
            "rating_range": f"{min_rating}-{max_rating}",
            "count": len(results),
            "films": results
        }


class SearchByActorTool(Tool):
    """Tool for searching films by actor."""
    
    def __init__(self, db: FilmsDatabase):
        self.db = db
    
    @property
    def name(self) -> str:
        return "search_by_actor"
    
    @property
    def description(self) -> str:
        return "Search for films featuring a specific actor. Supports partial name matches and is case-insensitive. Returns up to 20 films."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "actor_name": {
                "type": "string",
                "description": "The actor's name or partial name to search for",
                "required": True
            }
        }
    
    def execute(self, actor_name: str) -> Dict[str, Any]:
        """Execute actor search."""
        results = self.db.search_by_actor(actor_name)
        return {
            "success": True,
            "actor": actor_name,
            "count": len(results),
            "films": results
        }


def create_film_tools(db: FilmsDatabase) -> list[Tool]:
    """Create all film search tools."""
    return [
        SearchByTitleTool(db),
        FilterByGenreTool(db),
        SearchByRatingTool(db),
        SearchByActorTool(db)
    ]
