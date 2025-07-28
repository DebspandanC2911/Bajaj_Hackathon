import os
from dotenv import load_dotenv

def check_environment():
    """Check if environment variables are properly loaded"""
    
    print(" Checking environment setup...")
    
    # Load .env file
    load_dotenv()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print(".env file found")
        
        # Read and display .env contents (without showing the actual API key)
        with open('.env', 'r') as f:
            lines = f.readlines()
            print("\n .env file contents:")
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0]
                    if 'API_KEY' in key:
                        print(f"   {key}=***hidden***")
                    else:
                        print(f"   {line.strip()}")
    else:
        print(".env file not found!")
        print("   Please create a .env file in the project root with your OpenAI API key")
        return False
    
    # Check environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith('sk-'):
            print(" OPENAI_API_KEY loaded and looks valid")
        else:
            print("  OPENAI_API_KEY loaded but doesn't look like a valid OpenAI key")
            print("   OpenAI keys should start with 'sk-'")
    else:
        print("OPENAI_API_KEY not loaded from environment")
        return False
    
    # Check other variables
    other_vars = ["EMBEDDING_MODEL", "LLM_MODEL", "CHUNK_SIZE"]
    for var in other_vars:
        value = os.getenv(var)
        if value:
            print(f" {var}={value}")
        else:
            print(f"  {var} not set (will use default)")
    
    print("\n Environment setup looks good!")
    return True

if __name__ == "__main__":
    check_environment()
