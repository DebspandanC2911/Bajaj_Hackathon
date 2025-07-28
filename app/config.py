import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for the RAG PDF application"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # PDF Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Paths
    PDFS_FOLDER = "pdfs"
    EMBEDDINGS_FILE = "embeddings.pkl"
    DOCUMENTS_FILE = "documents.pkl"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        if not cls.GEMINI_API_KEY.startswith('AI'):
            logger.warning(
                "Gemini API key should typically start with 'AI'. "
                "Please verify your API key is correct."
            )
        
        logger.info("Configuration validated successfully")
        return True

# Validate configuration on import
Config.validate()
