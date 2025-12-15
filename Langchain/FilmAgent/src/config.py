"""Configuration management for the Film Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Token limits
MAX_CONTEXT_TOKENS = 30000
COMPRESSION_THRESHOLD = 25000

# Database Configuration
DATA_DIR = PROJECT_ROOT / "data"
FILMS_DB_PATH = DATA_DIR / "films.db"
MEMORY_DB_PATH = DATA_DIR / "memory.db"

# Logging Configuration
LOG_DIR = PROJECT_ROOT / "logs"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "agent.log"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


def validate_config():
    """Validate that required configuration is present."""
    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set it in .env file. "
            "Get your API key from: https://makersuite.google.com/app/apikey"
        )
    return True
