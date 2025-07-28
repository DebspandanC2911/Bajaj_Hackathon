import os
import asyncio
import requests
import json
from dotenv import load_dotenv
import google.generativeai as genai

async def diagnose_system():
    """Comprehensive system diagnosis"""
    
    print("🔍 RAG PDF System Diagnosis")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check 1: Environment variables
    print("1. 🔧 Checking Environment Variables...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   ✅ GEMINI_API_KEY found (starts with: {api_key[:5]}...)")
    else:
        print("   ❌ GEMINI_API_KEY not found")
        return False
    
    # Check 2: PDF files
    print("\n2. 📄 Checking PDF Files...")
    if os.path.exists('pdfs'):
        pdf_files = [f for f in os.listdir('pdfs') if f.lower().endswith('.pdf')]
        print(f"   ✅ Found {len(pdf_files)} PDF files: {pdf_files}")
        if len(pdf_files) == 0:
            print("   ⚠️  No PDF files found - this could be the issue!")
    else:
        print("   ❌ pdfs/ directory not found")
        return False
    
    # Check 3: Gemini API
    print("\n3. 🤖 Testing Gemini API...")
    try:
        genai.configure(api_key=api_key)
        
        # Test embedding
        result = genai.embed_content(
            model="models/embedding-001",
            content="test embedding",
            task_type="retrieval_document"
        )
        print("   ✅ Gemini embedding API working")
        
        # Test text generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        print("   ✅ Gemini text generation API working")
        
    except Exception as e:
        print(f"   ❌ Gemini API error: {e}")
        return False
    
    # Check 4: Server status
    print("\n4. 🌐 Checking Server Status...")
    try:
        response = requests.get("http://localhost:8000/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server responding")
            print(f"   📊 Documents: {data['documents_count']}")
            print(f"   📊 Chunks: {data['chunks_count']}")
            
            if data['documents_count'] == 0:
                print("   ⚠️  No documents processed - this is likely the issue!")
                return False
                
        else:
            print(f"   ❌ Server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server - is it running?")
        return False
    except Exception as e:
        print(f"   ❌ Server check error: {e}")
        return False
    
    # Check 5: Test simple query
    print("\n5. 🔍 Testing Simple Query...")
    try:
        query_data = {"query": "What is this document about?"}
        response = requests.post(
            "http://localhost:8000/query", 
            json=query_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['decision'] != 'Uncertain':
                print("   ✅ Query processing working")
                print(f"   📋 Decision: {result['decision']}")
            else:
                print("   ⚠️  Query returns 'Uncertain' - checking details...")
                print(f"   📝 Justification: {result['justification'][0]['text']}")
                return False
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Query test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All checks passed! System is working correctly.")
    return True

if __name__ == "__main__":
    success = asyncio.run(diagnose_system())
    
    if not success:
        print("\n🔧 Suggested Fixes:")
        print("1. Create sample PDF: python create_sample_pdf.py")
        print("2. Restart server: uvicorn app.main:app --reload")
        print("3. Trigger ingestion: curl -X POST http://localhost:8000/ingest")
        print("4. server logs for detailed errors")
