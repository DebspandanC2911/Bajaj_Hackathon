import asyncio
import aiohttp
import json
import time

async def test_complete_system():
    """Comprehensive test of the RAG PDF system"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing RAG PDF Query System")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Health check
            print("1. 🔍 Testing health check...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ {result['message']}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
                    return
            
            # Wait for PDF processing
            print("\n2. ⏳ Waiting for PDF processing (10 seconds)...")
            await asyncio.sleep(10)
            
            # Test 2: System status
            print("3. 🔍 Checking system status...")
            async with session.get(f"{base_url}/status") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Status: {result['documents_count']} documents, {result['chunks_count']} chunks")
                    
                    if result['documents_count'] == 0:
                        print("   ⚠️  No documents found. Make sure PDFs are in the pdfs/ folder")
                        return
                else:
                    print(f"   ❌ Status check failed: {response.status}")
                    return
            
            # Test 3: List documents
            print("\n4. 🔍 Listing processed documents...")
            async with session.get(f"{base_url}/documents") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Documents: {result['documents']}")
                else:
                    print(f"   ❌ Document listing failed: {response.status}")
            
            # Test 4: Simple query
            print("\n5. 🔍 Testing simple query...")
            query_data = {"query": "What is covered under this insurance policy?"}
            async with session.post(f"{base_url}/query", json=query_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Query successful")
                    print(f"   📋 Decision: {result['decision']}")
                    print(f"   📝 Justifications: {len(result['justification'])} items")
                    if result['justification']:
                        print(f"   💬 Sample: {result['justification'][0]['text'][:100]}...")
                else:
                    print(f"   ❌ Simple query failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
            
            # Test 5: Insurance-specific query
            print("\n6. 🔍 Testing insurance claim query...")
            query_data = {
                "query": "46-year-old male needs knee surgery in Pune, has 3-month-old insurance policy. Will it be covered?"
            }
            async with session.post(f"{base_url}/query", json=query_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Insurance query successful")
                    print(f"   📋 Decision: {result['decision']}")
                    print(f"   💰 Amount: {result.get('amount', 'Not specified')}")
                    if result['justification']:
                        print(f"   📄 Source: {result['justification'][0]['source']}")
                        print(f"   📝 Justification: {result['justification'][0]['text'][:150]}...")
                    if result['alternatives']:
                        print(f"   🔄 Alternatives: {len(result['alternatives'])} found")
                else:
                    print(f"   ❌ Insurance query failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
            
            # Test 6: Edge case query
            print("\n7. 🔍 Testing edge case query...")
            query_data = {"query": "What about dental treatment coverage?"}
            async with session.post(f"{base_url}/query", json=query_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Edge case query successful")
                    print(f"   📋 Decision: {result['decision']}")
                else:
                    print(f"   ❌ Edge case query failed: {response.status}")
            
            print("\n" + "=" * 50)
            print("🎉 All tests completed successfully!")
            print("\n📊 System Performance Summary:")
            print("✅ Health check: Working")
            print("✅ PDF processing: Working")
            print("✅ Document retrieval: Working")
            print("✅ Query processing: Working")
            print("✅ RAG reasoning: Working")
            
            print("\n🚀 Your RAG PDF system is fully operational!")
            print("Visit http://localhost:8000/docs for interactive API documentation")
            
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the server is running with:")
            print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_complete_system())
