# Intelligent Film Agent

A conversational AI agent powered by Google Gemini that helps users discover films. It features memory persistence, multi-tool capabilities, and context awareness.

## Features

- **Film Discovery**: Search by title, genre, rating, and actor.
- **Intelligent Conversations**: Powered by Gemini 1.5 Flash or local Ollama models.
- **Memory**: Remembers your name and preferences (genres, actors) across sessions.
- **Multi-Tool Chains**: Can handle complex queries like ("Find action movies with rating > 8").
- **Local Database**: Ships with a pre-seeded SQLite database of classic films.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings**
   - Copy `.env.example` to `.env`
   - Choose your provider:
     - **Gemini**: Set `LLM_PROVIDER=gemini` and add `GEMINI_API_KEY`
     - **Ollama**: Set `LLM_PROVIDER=ollama` (ensure Ollama is running)

4. **Run the Agent**
   ```bash
   python main.py
   ```

## Architecture

- **`src/agent.py`**: Main agent logic and orchestration.
- **`src/tools/`**: Film search tools.
- **`src/memory/`**: Short-term and long-term memory management.
- **`src/data/`**: Database interface and schema.
- **`src/middleware/`**: Logging and context optimization.

## Testing

Run the integration test suite:
```bash
python -m pytest tests/test_integration.py -v
```
