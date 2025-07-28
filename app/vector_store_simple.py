import numpy as np
import os
import logging
import pickle
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStoreSimple:
    def __init__(self):
        self.embeddings = []  # Store embeddings as numpy arrays
        self.documents = []   # Store document content and metadata
        self.openai_client = None
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.embeddings_path = "embeddings.pkl"
        self.documents_path = "documents.pkl"
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store and OpenAI client"""
        try:
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.openai_client = OpenAI(api_key=api_key)
            
            # Load existing data if available
            if os.path.exists(self.embeddings_path) and os.path.exists(self.documents_path):
                self._load_data()
            else:
                self.embeddings = []
                self.documents = []
            
            logger.info("Simple vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing simple vector store: {e}")
            raise
    
    def _load_data(self):
        """Load existing embeddings and documents"""
        try:
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded {len(self.documents)} documents from storage")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.embeddings = []
            self.documents = []
    
    def _save_data(self):
        """Save embeddings and documents"""
        try:
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
            with open(self.documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    async def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        try:
            if not documents:
                return
            
            for doc in documents:
                # Generate embedding
                embedding = await self._get_embedding(doc["content"])
                self.embeddings.append(np.array(embedding))
                
                # Store document with metadata
                doc_data = {
                    "content": doc["content"],
                    "source": doc["source"],
                    "page": doc["page"],
                    "chunk_id": doc["chunk_id"],
                    "chunk_index": doc.get("chunk_index", 0)
                }
                self.documents.append(doc_data)
            
            # Save data
            self._save_data()
            
            logger.info(f"Added {len(documents)} documents to simple vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to simple vector store: {e}")
            raise
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity"""
        try:
            if not self.embeddings:
                return []
            
            # Generate query embedding
            query_embedding = await self._get_embedding(query)
            query_vector = np.array(query_embedding).reshape(1, -1)
            
            # Convert embeddings to matrix
            embeddings_matrix = np.vstack(self.embeddings)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_vector, embeddings_matrix)[0]
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Format results
            search_results = []
            for idx in top_indices:
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    similarity = similarities[idx]
                    
                    result = {
                        "content": doc["content"],
                        "source": doc["source"],
                        "page": doc["page"],
                        "chunk_id": doc["chunk_id"],
                        "similarity": float(similarity),
                        "distance": 1 - float(similarity)
                    }
                    search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching simple vector store: {e}")
            raise
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def is_document_processed(self, filename: str) -> bool:
        """Check if a document has already been processed"""
        try:
            for doc in self.documents:
                if doc["source"] == filename:
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error checking if document is processed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the vector store"""
        try:
            unique_sources = set()
            for doc in self.documents:
                unique_sources.add(doc["source"])
            
            return {
                "chunks": len(self.documents),
                "documents": len(unique_sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"chunks": 0, "documents": 0}
    
    def list_documents(self) -> List[str]:
        """List all processed documents"""
        try:
            unique_sources = set()
            for doc in self.documents:
                unique_sources.add(doc["source"])
            
            return sorted(list(unique_sources))
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def close(self):
        """Close the vector store connection"""
        try:
            self._save_data()
            logger.info("Simple vector store closed")
        except Exception as e:
            logger.error(f"Error closing simple vector store: {e}")
