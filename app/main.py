from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from .config import Config
from .pdf_ingestor import PDFIngestor
from .vector_store import VectorStore
from .query_handler import QueryHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
pdf_ingestor = None
vector_store = None
query_handler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global pdf_ingestor, vector_store, query_handler
    
    try:
        logger.info("Starting RAG PDF Query API...")
        
        # Validate configuration
        Config.validate()
        
        # Initialize components
        vector_store = VectorStore()
        pdf_ingestor = PDFIngestor(vector_store)
        query_handler = QueryHandler(vector_store)
        
        # Process existing PDFs on startup
        await pdf_ingestor.process_pdfs_folder()
        logger.info("Application initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        # Cleanup if needed
        if vector_store:
            vector_store.close()
        logger.info("Application shutdown complete")

app = FastAPI(
    title="RAG PDF Query API",
    description="Process natural language queries over PDF documents using RAG with Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class JustificationItem(BaseModel):
    clause: str
    text: str
    source: str

class QueryResponse(BaseModel):
    decision: str
    amount: Optional[str] = None
    justification: List[JustificationItem]
    alternatives: List[JustificationItem] = []

class StatusResponse(BaseModel):
    status: str
    documents_count: int
    chunks_count: int

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Health check endpoint"""
    return {"message": "RAG PDF Query API is running with Gemini"}

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status and document count"""
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not initialized")
        
        stats = vector_store.get_stats()
        return StatusResponse(
            status="healthy",
            documents_count=stats.get("documents", 0),
            chunks_count=stats.get("chunks", 0)
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query against the PDF documents"""
    try:
        if not query_handler:
            raise HTTPException(status_code=503, detail="Query handler not initialized")
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Processing query: {request.query}")
        
        # Process the query
        result = await query_handler.process_query(request.query)
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@app.post("/ingest")
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """Manually trigger PDF ingestion from the pdfs/ folder"""
    try:
        if not pdf_ingestor:
            raise HTTPException(status_code=503, detail="PDF ingestor not initialized")
        
        background_tasks.add_task(pdf_ingestor.process_pdfs_folder)
        
        return {"message": "PDF ingestion started in background"}
        
    except Exception as e:
        logger.error(f"Error triggering ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """List all processed documents"""
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not initialized")
        
        documents = vector_store.list_documents()
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
