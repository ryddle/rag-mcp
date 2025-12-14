"""RAG MCP Server with Qdrant and local embeddings."""

import os
from typing import Any
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


# Configuration from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
DEFAULT_COLLECTION = os.getenv("DEFAULT_COLLECTION", "documents")

# Create server instance
server = Server("rag-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available RAG tools."""
    return [
        types.Tool(
            name="add_documents",
            description="Add documents to the RAG system. Supports text content and optional metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "The text content to index"
                                },
                                "metadata": {
                                    "type": "object",
                                    "description": "Optional metadata (e.g., source, date, tags)",
                                    "additionalProperties": True
                                }
                            },
                            "required": ["content"]
                        },
                        "description": "List of documents to add to the collection"
                    },
                    "collection": {
                        "type": "string",
                        "description": f"Collection name (default: {DEFAULT_COLLECTION})"
                    }
                },
                "required": ["documents"]
            },
        ),
        types.Tool(
            name="search",
            description="Search for documents similar to a query using semantic search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "collection": {
                        "type": "string",
                        "description": f"Collection name (default: {DEFAULT_COLLECTION})"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "minimum": 1,
                        "maximum": 50
                    },
                    "score_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score (0-1, default: 0.0)",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="list_collections",
            description="List all available collections in Qdrant.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="delete_collection",
            description="Delete a collection from Qdrant. Use with caution!",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {
                        "type": "string",
                        "description": "Collection name to delete"
                    }
                },
                "required": ["collection"]
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    
    if name == "add_documents":
        from .rag_engine import add_documents
        result = await add_documents(
            documents=arguments.get("documents", []),
            collection=arguments.get("collection", DEFAULT_COLLECTION)
        )
        return [types.TextContent(type="text", text=result)]
    
    elif name == "search":
        from .rag_engine import search_documents
        result = await search_documents(
            query=arguments.get("query"),
            collection=arguments.get("collection", DEFAULT_COLLECTION),
            limit=arguments.get("limit", 5),
            score_threshold=arguments.get("score_threshold", 0.0)
        )
        return [types.TextContent(type="text", text=result)]
    
    elif name == "list_collections":
        from .rag_engine import list_collections
        result = await list_collections()
        return [types.TextContent(type="text", text=result)]
    
    elif name == "delete_collection":
        from .rag_engine import delete_collection
        result = await delete_collection(
            collection=arguments.get("collection")
        )
        return [types.TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the RAG MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rag-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
