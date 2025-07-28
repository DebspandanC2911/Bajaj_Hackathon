import os
import sys
import asyncio
from dotenv import load_dotenv

def check_environment():
    """Comprehensive environment and setup check"""
    
    print("🔍 RAG PDF Backend Setup Check")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    success = True
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} is too old. Need 3.8+")
        success = False
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            if api_key.startswith('AI'):
                print("✅ GEMINI_API_KEY loaded and looks valid")
            else:
                print("⚠️  GEMINI_API_KEY loaded but doesn't look like a valid Gemini key")
                print("   Gemini keys typically start with 'AI'")
        else:
            print("❌ GEMINI_API_KEY not found in .env file")
            success = False
    else:
        print("❌ .env file not found")
        print("   Please create a .env file with your Gemini API key")
        success = False
    
    # Check required directories
    if os.path.exists('pdfs'):
        pdf_files = [f for f in os.listdir('pdfs') if f.lower().endswith('.pdf')]
        print(f"✅ pdfs/ directory exists with {len(pdf_files)} PDF files")
    else:
        print("⚠️  pdfs/ directory not found - will be created automatically")
    
    if os.path.exists('app'):
        print("✅ app/ directory exists")
    else:
        print("❌ app/ directory not found")
        success = False
    
    # Check required Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'pymupdf', 
        'scikit-learn', 'google.generativeai', 'python-dotenv', 'numpy'
    ]
    
    print("\n📦 Checking Python packages:")
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai
                print(f"✅ {package}")
            elif package == 'pymupdf':
                import fitz
                print(f"✅ {package} (fitz)")
            else:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 All checks passed! You can start the server.")
        print("\nNext steps:")
        print("1. Make sure you have PDF files in the pdfs/ folder")
        print("2. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("3. Visit: http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nTo install missing packages:")
        print("pip install -r requirements.txt")
    
    return success

async def test_gemini_api():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Cannot test Gemini API - no API key found")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test embedding
        result = genai.embed_content(
            model="models/embedding-001",
            content="Test embedding",
            task_type="retrieval_document"
        )
        
        if result and 'embedding' in result:
            print("✅ Gemini embedding API working")
        else:
            print("❌ Gemini embedding API test failed")
            return False
        
        # Test text generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        
        if response and response.text:
            print("✅ Gemini text generation API working")
            return True
        else:
            print("❌ Gemini text generation API test failed")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    if check_environment():
        print("\n🔍 Testing Gemini API connection...")
        api_success = asyncio.run(test_gemini_api())
        
        if api_success:
            print("\n🚀 Everything is ready! You can start the server now.")
        else:
            print("\n⚠️  Environment setup is correct but API test failed.")
            print("Please check your Gemini API key and internet connection.")
