import faiss
import numpy as np
import os
import logging
import pickle
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStoreFAISS:
    def __init__(self):
        self.index = None
        self.documents = []  # Store document content and metadata
        self.openai_client = None
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.index_path = "faiss_index"
        self.documents_path = "documents.pkl"
        self.dimension = 1536  # OpenAI embedding dimension
        
        self._initialize()
    
    def _initialize(self):
        """Initialize FAISS index and OpenAI client"""
        try:
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.openai_client = OpenAI(api_key=api_key)
            
            # Create or load FAISS index
            if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
                self._load_index()
            else:
                self._create_new_index()
            
            logger.info("FAISS vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing FAISS vector store: {e}")
            raise
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.documents = []
    
    def _load_index(self):
        """Load existing FAISS index and documents"""
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self._create_new_index()
    
    def _save_index(self):
        """Save FAISS index and documents"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    async def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the FAISS vector store"""
        try:
            if not documents:
                return
            
            embeddings = []
            for doc in documents:
                # Generate embedding
                embedding = await self._get_embedding(doc["content"])
                embeddings.append(embedding)
                
                # Store document with metadata
                doc_data = {
                    "content": doc["content"],
                    "source": doc["source"],
                    "page": doc["page"],
                    "chunk_id": doc["chunk_id"],
                    "chunk_index": doc.get("chunk_index", 0)
                }
                self.documents.append(doc_data)
            
            # Convert to numpy array and normalize for cosine similarity
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss.normalize_L2(embeddings_array)
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Save index
            self._save_index()
            
            logger.info(f"Added {len(documents)} documents to FAISS vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to FAISS vector store: {e}")
            raise
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using FAISS"""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = await self._get_embedding(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search in FAISS
            similarities, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            # Format results
            search_results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.documents):
                    doc = self.documents[idx]
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
            logger.error(f"Error searching FAISS vector store: {e}")
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
            self._save_index()
            logger.info("FAISS vector store closed")
        except Exception as e:
            logger.error(f"Error closing FAISS vector store: {e}")
