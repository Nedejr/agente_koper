"""
Retriever
Semantic search and document retrieval from Qdrant
"""

from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.rag.embeddings import embeddings_generator
from backend.rag.vector_store import vector_store_client
from backend.utils.logger import log


class Retriever:
    """
    Retrieves relevant documents using semantic search
    """
    
    def __init__(
        self,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ):
        self.top_k = top_k or settings.top_k_results
        self.score_threshold = score_threshold or settings.min_similarity_score
        
        log.info(
            f"🔍 Retriever initialized - "
            f"Top K: {self.top_k} | "
            f"Score threshold: {self.score_threshold}"
        )
    
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filters: Additional filters for search
            
        Returns:
            List of retrieved documents with scores
        """
        try:
            top_k = top_k or self.top_k
            score_threshold = score_threshold or self.score_threshold
            
            log.info(f"🔍 Retrieving documents for query: '{query[:50]}...'")
            
            # Generate query embedding
            query_embedding = embeddings_generator.generate_single(query)
            
            # Search in vector store
            results = await vector_store_client.search(
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                filter_conditions=filters,
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result["payload"].get("content", ""),
                    "metadata": result["payload"].get("metadata", {}),
                    "score": result["score"],
                    "id": result["id"],
                })
            
            log.info(f"✅ Retrieved {len(formatted_results)} documents")
            
            return formatted_results
            
        except Exception as e:
            log.error(f"❌ Error retrieving documents: {str(e)}")
            raise
    
    async def retrieve_with_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Retrieve documents and format as context for LLM
        
        Args:
            query: Search query
            top_k: Number of results
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with formatted context and metadata
        """
        results = await self.retrieve(query, top_k, **kwargs)
        
        if not results:
            return {
                "context": "No relevant documents found.",
                "documents": [],
                "avg_score": 0.0,
                "total_results": 0,
            }
        
        # Format context for LLM
        context_parts = []
        for i, doc in enumerate(results, 1):
            content = doc["content"]
            source = doc["metadata"].get("filename", "Unknown")
            context_parts.append(f"[Document {i} - {source}]\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Calculate average score
        avg_score = sum(doc["score"] for doc in results) / len(results)
        
        return {
            "context": context,
            "documents": results,
            "avg_score": avg_score,
            "total_results": len(results),
        }
    
    async def retrieve_by_filters(
        self,
        filters: Dict[str, Any],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents by metadata filters only (no semantic search)
        
        Args:
            filters: Metadata filters
            top_k: Number of results
            
        Returns:
            List of filtered documents
        """
        # This would require a different Qdrant query
        # For now, not implemented
        raise NotImplementedError("Filter-only retrieval not yet implemented")
    
    def format_documents_for_prompt(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents for use in prompts
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted string for prompt
        """
        if not documents:
            return "No relevant documents found."
        
        formatted = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            score = doc.get("score", 0.0)
            
            source = metadata.get("filename", "Unknown source")
            
            formatted.append(
                f"[Document {i}] (Relevance: {score:.2f})\n"
                f"Source: {source}\n"
                f"Content: {content}\n"
            )
        
        return "\n---\n".join(formatted)
    
    async def get_retrieval_stats(self, query: str) -> Dict[str, Any]:
        """
        Get statistics about retrieval for a query
        
        Args:
            query: Search query
            
        Returns:
            Statistics dictionary
        """
        results = await self.retrieve(query)
        
        if not results:
            return {
                "query": query,
                "total_results": 0,
                "avg_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
            }
        
        scores = [doc["score"] for doc in results]
        
        return {
            "query": query,
            "total_results": len(results),
            "avg_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
        }


# Singleton instance
retriever = Retriever()

