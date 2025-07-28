# RAG PDF Query API

A backend-only Python project that exposes a REST API to process natural language queries over unstructured PDF documents using LLMs, vector embeddings, and Retrieval-Augmented Generation (RAG).

## Features

- 📂 **PDF Ingestion**: Automatically processes PDFs from the `pdfs/` folder
- 🔍 **Natural Language Queries**: Process complex queries using LLMs
- 🧠 **RAG-based Reasoning**: Combines vector search with LLM reasoning
- 📤 **Structured Responses**: Returns decisions with justifications and alternatives
- 🚀 **FastAPI**: High-performance REST API with automatic documentation

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd rag-pdf-backend

# Install dependencies
pip install -r requirements.txt
Then run-

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
