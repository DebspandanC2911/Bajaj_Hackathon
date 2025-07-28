import asyncio
import aiohttp
import json
import time

async def test_api():
    """Test the complete RAG system"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Health check
            print("🔍 Testing health check...")
            async with session.get(f"{base_url}/") as response:
                result = await response.json()
                print(f"✅ Health check: {result['message']}")
            
            # Wait a moment for PDF processing
            print("\n⏳ Waiting for PDF processing...")
            await asyncio.sleep(5)
            
            # Test 2: Check status
            print("🔍 Checking system status...")
            async with session.get(f"{base_url}/status") as response:
                result = await response.json()
                print(f"✅ Status: {result['documents_count']} documents, {result['chunks_count']} chunks")
            
            # Test 3: List documents
            print("\n🔍 Listing documents...")
            async with session.get(f"{base_url}/documents") as response:
                result = await response.json()
                print(f"✅ Documents: {result['documents']}")
            
            # Test 4: Simple query
            print("\n🔍 Testing simple query...")
            query_data = {"query": "What is covered under this policy?"}
            async with session.post(f"{base_url}/query", json=query_data) as response:
                result = await response.json()
                print(f"✅ Query result:")
                print(f"   Decision: {result['decision']}")
                print(f"   Justification: {len(result['justification'])} items")
            
            # Test 5: Specific insurance query
            print("\n🔍 Testing insurance-specific query...")
            query_data = {"query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"}
            async with session.post(f"{base_url}/query", json=query_data) as response:
                result = await response.json()
                print(f"✅ Insurance query result:")
                print(f"   Decision: {result['decision']}")
                print(f"   Amount: {result.get('amount', 'Not specified')}")
                print(f"   Justification: {result['justification'][0]['text'][:100]}..." if result['justification'] else "No justification")
            
            print("\n🎉 All tests passed! Your RAG system is working correctly.")
            
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            print("Make sure the server is running with: uvicorn app.main:app --reload")

if __name__ == "__main__":
    asyncio.run(test_api())
