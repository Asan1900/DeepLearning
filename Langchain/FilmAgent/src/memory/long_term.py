"""Long-term memory for user preferences and profile."""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from datetime import datetime

from ..config import MEMORY_DB_PATH


class LongTermMemory:
    """Manages long-term user preferences and profile."""
    
    def __init__(self, db_path: Path = MEMORY_DB_PATH):
        self.db_path = db_path
        self._initialize_db()
        self.current_user_id: Optional[int] = None
    
    def _initialize_db(self):
        """Initialize database with schema if it doesn't exist."""
        schema_path = Path(__file__).parent / "schema.sql"
        
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
    
    def get_or_create_user(self, name: Optional[str] = None) -> int:
        """Get or create a user, return user_id."""
        with self._get_connection() as conn:
            if name:
                # Try to find existing user by name
                cursor = conn.execute(
                    "SELECT id FROM users WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                if row:
                    user_id = row['id']
                    # Update last_active
                    conn.execute(
                        "UPDATE users SET last_active = ? WHERE id = ?",
                        (datetime.now(), user_id)
                    )
                    conn.commit()
                    self.current_user_id = user_id
                    return user_id
            
            # Create new user
            cursor = conn.execute(
                "INSERT INTO users (name) VALUES (?)",
                (name,)
            )
            conn.commit()
            self.current_user_id = cursor.lastrowid
            return cursor.lastrowid
    
    def set_user_name(self, user_id: int, name: str):
        """Set or update user name."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE users SET name = ? WHERE id = ?",
                (name, user_id)
            )
            conn.commit()
    
    def get_user_name(self, user_id: int) -> Optional[str]:
        """Get user name."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row['name'] if row else None
    
    def add_preference(self, user_id: int, preference_type: str, 
                      preference_value: str, confidence: float = 1.0):
        """Add or update a user preference."""
        with self._get_connection() as conn:
            # Check if preference already exists
            cursor = conn.execute(
                """
                SELECT id FROM preferences 
                WHERE user_id = ? AND preference_type = ? AND preference_value = ?
                """,
                (user_id, preference_type, preference_value)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update confidence and timestamp
                conn.execute(
                    """
                    UPDATE preferences 
                    SET confidence = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (confidence, datetime.now(), existing['id'])
                )
            else:
                # Insert new preference
                conn.execute(
                    """
                    INSERT INTO preferences 
                    (user_id, preference_type, preference_value, confidence)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, preference_type, preference_value, confidence)
                )
            conn.commit()
    
    def get_preferences(self, user_id: int, 
                       preference_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user preferences, optionally filtered by type."""
        with self._get_connection() as conn:
            if preference_type:
                cursor = conn.execute(
                    """
                    SELECT preference_type, preference_value, confidence, updated_at
                    FROM preferences
                    WHERE user_id = ? AND preference_type = ?
                    ORDER BY confidence DESC, updated_at DESC
                    """,
                    (user_id, preference_type)
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT preference_type, preference_value, confidence, updated_at
                    FROM preferences
                    WHERE user_id = ?
                    ORDER BY preference_type, confidence DESC, updated_at DESC
                    """,
                    (user_id,)
                )
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_context(self, user_id: int) -> str:
        """Generate a context string with user information and preferences."""
        name = self.get_user_name(user_id)
        preferences = self.get_preferences(user_id)
        
        context_parts = []
        
        if name:
            context_parts.append(f"User name: {name}")
        
        if preferences:
            context_parts.append("\nUser preferences:")
            
            # Group by type
            prefs_by_type: Dict[str, List[str]] = {}
            for pref in preferences:
                pref_type = pref['preference_type']
                pref_value = pref['preference_value']
                if pref_type not in prefs_by_type:
                    prefs_by_type[pref_type] = []
                prefs_by_type[pref_type].append(pref_value)
            
            for pref_type, values in prefs_by_type.items():
                context_parts.append(f"  - {pref_type}: {', '.join(values)}")
        
        return "\n".join(context_parts) if context_parts else "No user context available."
    
    def save_conversation_turn(self, user_id: int, role: str, content: str, 
                              tool_name: Optional[str] = None):
        """Save a conversation turn to long-term storage."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversations (user_id, role, content, tool_name)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, role, content, tool_name)
            )
            conn.commit()
    
    def get_conversation_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve conversation history from long-term storage."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT role, content, tool_name, created_at
                FROM conversations
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()][::-1]  # Reverse to chronological order
