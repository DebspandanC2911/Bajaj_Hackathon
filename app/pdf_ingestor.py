import os
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any
import asyncio
from pathlib import Path
from .config import Config

logger = logging.getLogger(__name__)

class PDFIngestor:
    """PDF ingestion and processing class"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.pdfs_folder = Config.PDFS_FOLDER
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
        
        # Create pdfs folder if it doesn't exist
        os.makedirs(self.pdfs_folder, exist_ok=True)
        
    async def process_pdfs_folder(self):
        """Process all PDFs in the pdfs/ folder"""
        try:
            pdf_files = [f for f in os.listdir(self.pdfs_folder) 
                        if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                logger.info("No PDF files found in pdfs/ folder")
                return
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(self.pdfs_folder, pdf_file)
                try:
                    # Check if document is already processed
                    if self.vector_store.is_document_processed(pdf_file):
                        logger.info(f"Skipping {pdf_file} - already processed")
                        continue
                    
                    logger.info(f"Processing {pdf_file}")
                    await self.process_pdf(pdf_path)
                    logger.info(f"Successfully processed {pdf_file}")
                    
                except Exception as e:
                    logger.error(f"Error processing {pdf_file}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing PDFs folder: {e}")
            raise
    
    async def process_pdf(self, pdf_path: str):
        """Process a single PDF file"""
        try:
            # Extract text from PDF
            text_chunks = self.extract_text_from_pdf(pdf_path)
            
            if not text_chunks:
                logger.warning(f"No text extracted from {pdf_path}")
                return
            
            # Create chunks with metadata
            chunks_with_metadata = []
            filename = os.path.basename(pdf_path)
            
            for chunk_data in text_chunks:
                chunk_id = self.generate_chunk_id(
                    filename, chunk_data['page'], chunk_data['chunk_index']
                )
                
                metadata = {
                    "content": chunk_data['text'],
                    "source": filename,
                    "page": chunk_data['page'],
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_data['chunk_index']
                }
                
                chunks_with_metadata.append(metadata)
            
            # Store in vector database
            await self.vector_store.add_documents(chunks_with_metadata)
            
            logger.info(f"Added {len(chunks_with_metadata)} chunks from {filename}")
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF and create chunks"""
        chunks = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # Split text into chunks
                page_chunks = self.create_chunks(text, page_num + 1)
                chunks.extend(page_chunks)
            
            doc.close()
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    def create_chunks(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Create overlapping chunks from text"""
        chunks = []
        
        # Clean and prepare text
        text = text.strip()
        if not text:
            return chunks
        
        # Simple sentence-based chunking
        sentences = text.split('. ')
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed chunk size
            potential_chunk = (current_chunk + ". " + sentence 
                             if current_chunk else sentence)
            
            if len(potential_chunk) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'text': current_chunk.strip(),
                    'page': page_num,
                    'chunk_index': chunk_index
                })
                
                # Start new chunk with overlap
                overlap_text = self.get_overlap_text(current_chunk)
                current_chunk = (overlap_text + ". " + sentence 
                               if overlap_text else sentence)
                chunk_index += 1
            else:
                current_chunk = potential_chunk
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'page': page_num,
                'chunk_index': chunk_index
            })
        
        return chunks
    
    def get_overlap_text(self, text: str) -> str:
        """Get overlap text for chunk continuity"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Get last chunk_overlap characters, but try to break at sentence boundary
        overlap_text = text[-self.chunk_overlap:]
        
        # Find the last sentence boundary
        last_period = overlap_text.rfind('. ')
        if last_period > 0:
            overlap_text = overlap_text[last_period + 2:]
        
        return overlap_text.strip()
    
    def generate_chunk_id(self, filename: str, page: int, chunk_index: int) -> str:
        """Generate a unique chunk ID"""
        base_name = os.path.splitext(filename)[0]
        return f"{base_name}-p{page}-c{chunk_index}"
