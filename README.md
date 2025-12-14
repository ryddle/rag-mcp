# RAG MCP Server

A Model Context Protocol (MCP) server that provides RAG (Retrieval-Augmented Generation) capabilities using local embeddings and Qdrant vector database.

## Features

- 🔍 **Semantic Search**: Search documents using natural language queries
- 📚 **Document Management**: Add, search, and manage documents in collections
- 🤖 **Local Embeddings**: Uses Ollama with configurable embedding models (default: nomic-embed-text)
- 💾 **Qdrant Integration**: Fast and efficient vector storage and retrieval
- 🔧 **Configurable**: Easy configuration via environment variables

## Prerequisites

- Python 3.10+
- **Embedding Provider** (choose one):
  - [Ollama](https://ollama.ai) running locally, OR
  - [LMStudio](https://lmstudio.ai) running locally
- [Qdrant](https://qdrant.tech) running (e.g., via Docker)

### Start Qdrant with Docker

```bash
docker run -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

### Setup Embedding Provider

**Option A: Using Ollama**
```bash
# Pull the embedding model
ollama pull nomic-embed-text

# Start Ollama (if not already running)
ollama serve
```

**Option B: Using LMStudio**
1. Open LMStudio
2. Download an embedding model (e.g., `nomic-embed-text-v1.5`)
3. Start the Local Server on port 1234
4. Load the embedding model

## Installation

1. Clone the repository:
```bash
git clone <your-repo>
### For Ollama:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333

# Embedding Provider
EMBEDDING_PROVIDER=ollama
EMBEDDING_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text

# Default Collection
DEFAULT_COLLECTION=documents
```

### For LMStudio:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333

# Embedding Provider
EMBEDDING_PROVIDER=lmstudio
EMBEDDING_BASE_URL=http://localhost:1234
EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5

3. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

## Configuration

Create a `.env` file or set environment variables:

```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text

# Default Collection
DEFAULT_COLLECTION=documents
```

### Supported Embedding Models

The server is designed to work with any Ollama-compatible embedding model:

- **nomic-embed-text** (default): 768d, 8192 context, requires task prefixes
- **qwen3-embedding-0.6b**: 1024d, 32k context, multilingual
- **qwen3-embedding-4b**: 2560d, 32k context, top performance
- **embeddinggemma-300m**: 768d, 2048 context, lightweight

Change the model by setting `EMBEDDING_MODEL` in your `.env` file.

## Available Tools

### 1. `add_documents`
Add documents to the RAG system with optional metadata.

**Parameters:**
- `documents` (array, required): List of documents to add
  - `content` (string, required): The text content to index
  - `metadata` (object, optional): Additional metadata (source, date, tags, etc.)
- `collection` (string, optional): Collection name (default: "documents")

**Example:**
```json
{
  "documents": [
    {
      "content": "Python is a high-level programming language.",
      "metadata": {"source": "wiki", "topic": "programming"}
    }
  ],
  "collection": "knowledge"
}
```

### 2. `search`
Search for documents similar to a query using semantic search.

**Parameters:**
- `query` (string, required): The search query
- `collection` (string, optional): Collection name (default: "documents")
- `limit` (integer, optional): Maximum results (1-50, default: 5)
- `score_threshold` (number, optional): Minimum similarity score (0-1, default: 0.0)

**Example:**
```json
{
  "query": "What is Python?",
  "collection": "knowledge",
  "limit": 3,
  "score_threshold": 0.7
}
```

### 3. `list_collections`
List all available collections in Qdrant.

**Parameters:** None

### 4. `delete_collection`
Delete a collection from Qdrant. ⚠️ Use with caution!

**Parameters:**
- `collection` (string, required): Collection name to delete

## Usage MCP

Add to your LMStudio MCP configuration:

**Using Ollama for embeddings:**
```json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/rag-mcp",
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_BASE_URL": "http://localhost:11434",
        "EMBEDDING_MODEL": "nomic-embed-text"
      }
    }
  }
}
```

**Using LMStudio for embeddings:**
```json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/rag-mcp",
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "EMBEDDING_PROVIDER": "lmstudio",
        "EMBEDDING_BASE_URL": "http://localhost:1234",
        "EMBEDDING_MODEL": "text-embedding-nomic-embed-text-v1.5

### Using with LMStudio

Add to your LMStudio MCP configuration:

```json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/rag-mcp",
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "EMBEDDING_MODEL": "nomic-embed-text"
      }
    }
  }
}
```

## Example Workflow

1. **Add documents to the knowledge base:**
```python
# Use add_documents tool
{
  "documents": [
    {"content": "MCP is a protocol for AI tools"},
    {"content": "Qdrant is a vector database"},
    {"content": "Ollama runs local AI models"}
  ]
}
```

2. **Search for relevant information:**
```python
# Use search tool
{Embedding Provider Issues

**Ollama:**
- Ensure Ollama is running: `ollama serve`
- Check the model is pulled: `ollama list`
- Verify `EMBEDDING_BASE_URL` is correct (default: `http://localhost:11434`)

**LMStudio:**
- Ensure LMStudio Local Server is running
- Verify the embedding model is loaded in LMStudio
- Check `EMBEDDING_BASE_URL` is correct (default: `http://localhost:1234`)
- Ensure CORS is enabled if needed

### Qdrant Connection Issues
- Ensure Qdrant is running on port 6333
- Check Docker logs: `docker logs <qdrant-container-id>`
- Verify `QDRANT_URL` is correct

### Embedding Errors
- nomic-embed-text requires task prefixes (handled automatically)
- Make sure `EMBEDDING_PROVIDER` is set correctly ("ollama" or "lmstudio"
## Development

### Project Structure

```
rag-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py       # MCP server implementation
│   └── rag_engine.py   # RAG logic (embeddings, Qdrant)
├── pyproject.toml      # Project configuration
├── .env.example        # Environment variables template
└── README.md
```

### Adding New Features

The server is designed to be extensible. To add new tools:

1. Add the tool definition in `server.py` (`handle_list_tools`)
2. Implement the handler in `server.py` (`handle_call_tool`)
3. Add the business logic in `rag_engine.py`

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check the model is pulled: `ollama pull nomic-embed-text`
- Verify `OLLAMA_BASE_URL` is correct

### Qdrant Connection Issues
- Ensure Qdrant is running on port 6333
- Check Docker logs: `docker logs <qdrant-container-id>`
- Verify `QDRANT_URL` is correct

### Embedding Errors
- nomic-embed-text requires task prefixes (handled automatically)
- For other models, you may need to adjust the prefix logic in `rag_engine.py`

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
