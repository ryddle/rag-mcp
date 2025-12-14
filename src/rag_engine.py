"""RAG Engine - handles embeddings, Qdrant operations, and document processing."""

import os
import json
import uuid
from typing import List, Dict, Any
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")  # "ollama" or "lmstudio"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_DIM = 768  # nomic-embed-text dimension

# Initialize Qdrant client
qdrant = QdrantClient(url=QDRANT_URL)


async def get_embedding(text: str, task_prefix: str = "search_document") -> List[float]:
    """
    Get embedding for text using Ollama or LMStudio.
    
    Args:
        text: Text to embed
        task_prefix: Task prefix for nomic-embed (search_document, search_query, etc.)
    
    Returns:
        List of floats representing the embedding
    """
    # Add task prefix for nomic-embed-text
    if "nomic" in EMBEDDING_MODEL.lower():
        prefixed_text = f"{task_prefix}: {text}"
    else:
        prefixed_text = text
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if EMBEDDING_PROVIDER.lower() == "lmstudio":
            # LMStudio uses OpenAI-compatible API
            response = await client.post(
                f"{EMBEDDING_BASE_URL}/v1/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "input": prefixed_text
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        else:
            # Ollama API
            response = await client.post(
                f"{EMBEDDING_BASE_URL}/api/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": prefixed_text
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]


async def ensure_collection(collection_name: str) -> None:
    """Ensure a collection exists in Qdrant."""
    try:
        collections = qdrant.get_collections().collections
        if not any(c.name == collection_name for c in collections):
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
            )
    except Exception as e:
        raise Exception(f"Failed to ensure collection: {str(e)}")


async def add_documents(documents: List[Dict[str, Any]], collection: str) -> str:
    """
    Add documents to the RAG system.
    
    Args:
        documents: List of documents with 'content' and optional 'metadata'
        collection: Collection name
    
    Returns:
        Success message with count
    """
    try:
        await ensure_collection(collection)
        
        points = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Get embedding
            embedding = await get_embedding(content, task_prefix="search_document")
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata
                }
            )
            points.append(point)
        
        # Upsert to Qdrant
        qdrant.upsert(collection_name=collection, points=points)
        
        return json.dumps({
            "success": True,
            "message": f"Added {len(documents)} document(s) to collection '{collection}'",
            "count": len(documents)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def search_documents(
    query: str,
    collection: str,
    limit: int = 5,
    score_threshold: float = 0.0
) -> str:
    """
    Search for similar documents.
    
    Args:
        query: Search query
        collection: Collection name
        limit: Max results
        score_threshold: Minimum similarity score
    
    Returns:
        JSON string with search results
    """
    try:
        # Get query embedding
        query_embedding = await get_embedding(query, task_prefix="search_query")
        
        # Search in Qdrant using query_points
        from qdrant_client.models import QueryRequest, QueryResponse
        
        results = qdrant.query_points(
            collection_name=collection,
            query=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        ).points
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result.score,
                "content": result.payload.get("content", ""),
                "metadata": result.payload.get("metadata", {}),
                "id": result.id
            })
        
        return json.dumps({
            "success": True,
            "query": query,
            "collection": collection,
            "count": len(formatted_results),
            "results": formatted_results
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def list_collections() -> str:
    """List all collections in Qdrant."""
    try:
        collections = qdrant.get_collections().collections
        
        collection_info = []
        for col in collections:
            info = qdrant.get_collection(col.name)
            collection_info.append({
                "name": col.name,
                "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else info.points_count,
                "points_count": info.points_count
            })
        
        return json.dumps({
            "success": True,
            "count": len(collection_info),
            "collections": collection_info
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def delete_collection(collection: str) -> str:
    """Delete a collection from Qdrant."""
    try:
        qdrant.delete_collection(collection_name=collection)
        
        return json.dumps({
            "success": True,
            "message": f"Collection '{collection}' deleted successfully"
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)
