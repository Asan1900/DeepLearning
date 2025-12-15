"""Film database interface."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from ..config import FILMS_DB_PATH


class FilmsDatabase:
    """Interface for querying the films database."""
    
    def __init__(self, db_path: Path = FILMS_DB_PATH):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database with schema if it doesn't exist."""
        schema_path = Path(__file__).parent / "films_schema.sql"
        
        with self._get_connection() as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        return dict(row)
    
    def search_by_title(self, title: str) -> List[Dict[str, Any]]:
        """Search films by title (case-insensitive, partial match)."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT f.id, f.title, f.year, f.rating, f.description
                FROM films f
                WHERE LOWER(f.title) LIKE LOWER(?)
                ORDER BY f.rating DESC
                LIMIT 10
                """,
                (f"%{title}%",)
            )
            films = [self._row_to_dict(row) for row in cursor.fetchall()]
            
            # Enrich with genres and actors
            for film in films:
                film['genres'] = self._get_film_genres(film['id'])
                film['actors'] = self._get_film_actors(film['id'])
            
            return films
    
    def filter_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Get films by genre."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT f.id, f.title, f.year, f.rating, f.description
                FROM films f
                JOIN film_genres fg ON f.id = fg.film_id
                JOIN genres g ON fg.genre_id = g.id
                WHERE LOWER(g.name) = LOWER(?)
                ORDER BY f.rating DESC
                LIMIT 20
                """,
                (genre,)
            )
            films = [self._row_to_dict(row) for row in cursor.fetchall()]
            
            for film in films:
                film['genres'] = self._get_film_genres(film['id'])
                film['actors'] = self._get_film_actors(film['id'])
            
            return films
    
    def search_by_rating(self, min_rating: float, max_rating: float = 10.0) -> List[Dict[str, Any]]:
        """Search films by rating range."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT f.id, f.title, f.year, f.rating, f.description
                FROM films f
                WHERE f.rating BETWEEN ? AND ?
                ORDER BY f.rating DESC
                LIMIT 20
                """,
                (min_rating, max_rating)
            )
            films = [self._row_to_dict(row) for row in cursor.fetchall()]
            
            for film in films:
                film['genres'] = self._get_film_genres(film['id'])
                film['actors'] = self._get_film_actors(film['id'])
            
            return films
    
    def search_by_actor(self, actor_name: str) -> List[Dict[str, Any]]:
        """Search films by actor name."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT f.id, f.title, f.year, f.rating, f.description
                FROM films f
                JOIN film_actors fa ON f.id = fa.film_id
                JOIN actors a ON fa.actor_id = a.id
                WHERE LOWER(a.name) LIKE LOWER(?)
                ORDER BY f.rating DESC
                LIMIT 20
                """,
                (f"%{actor_name}%",)
            )
            films = [self._row_to_dict(row) for row in cursor.fetchall()]
            
            for film in films:
                film['genres'] = self._get_film_genres(film['id'])
                film['actors'] = self._get_film_actors(film['id'])
            
            return films
    
    def _get_film_genres(self, film_id: int) -> List[str]:
        """Get all genres for a film."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT g.name
                FROM genres g
                JOIN film_genres fg ON g.id = fg.genre_id
                WHERE fg.film_id = ?
                """,
                (film_id,)
            )
            return [row['name'] for row in cursor.fetchall()]
    
    def _get_film_actors(self, film_id: int) -> List[str]:
        """Get all actors for a film."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT a.name
                FROM actors a
                JOIN film_actors fa ON a.id = fa.actor_id
                WHERE fa.film_id = ?
                ORDER BY a.name
                """,
                (film_id,)
            )
            return [row['name'] for row in cursor.fetchall()]
    
    def add_film(self, title: str, year: int, rating: float, description: str,
                 genres: List[str], actors: List[str]) -> int:
        """Add a new film to the database."""
        with self._get_connection() as conn:
            # Insert film
            cursor = conn.execute(
                "INSERT INTO films (title, year, rating, description) VALUES (?, ?, ?, ?)",
                (title, year, rating, description)
            )
            film_id = cursor.lastrowid
            
            # Add genres
            for genre_name in genres:
                # Get or create genre
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO genres (name) VALUES (?)",
                    (genre_name,)
                )
                cursor = conn.execute(
                    "SELECT id FROM genres WHERE name = ?",
                    (genre_name,)
                )
                genre_id = cursor.fetchone()['id']
                
                # Link film to genre
                conn.execute(
                    "INSERT INTO film_genres (film_id, genre_id) VALUES (?, ?)",
                    (film_id, genre_id)
                )
            
            # Add actors
            for actor_name in actors:
                # Get or create actor
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO actors (name) VALUES (?)",
                    (actor_name,)
                )
                cursor = conn.execute(
                    "SELECT id FROM actors WHERE name = ?",
                    (actor_name,)
                )
                actor_id = cursor.fetchone()['id']
                
                # Link film to actor
                conn.execute(
                    "INSERT INTO film_actors (film_id, actor_id) VALUES (?, ?)",
                    (film_id, actor_id)
                )
            
            conn.commit()
            return film_id
    
    def get_all_genres(self) -> List[str]:
        """Get all available genres."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT name FROM genres ORDER BY name")
            return [row['name'] for row in cursor.fetchall()]
