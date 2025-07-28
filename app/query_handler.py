import os
import logging
from typing import List, Dict, Any
import json
import re
import google.generativeai as genai
from .config import Config

logger = logging.getLogger(__name__)

class QueryHandler:
    """Handle natural language queries using RAG with Gemini - Fixed Version"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm_model = Config.LLM_MODEL
        self.top_k = Config.TOP_K_RESULTS
        
        # Configure Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.llm_model)
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query using RAG"""
        try:
            logger.info(f"Starting query processing for: {query}")
            
            # Step 1: Parse the query to extract structured information
            structured_info = await self._parse_query(query)
            logger.info(f"Structured info extracted: {structured_info}")
            
            # Step 2: Search for relevant documents
            search_results = await self.vector_store.search(query, self.top_k)
            logger.info(f"Found {len(search_results)} relevant chunks")
            
            if not search_results:
                logger.warning("No search results found")
                return {
                    "decision": "Unknown",
                    "amount": None,
                    "justification": [{
                        "clause": "N/A", 
                        "text": "No relevant clause found in provided documents.", 
                        "source": "N/A"
                    }],
                    "alternatives": []
                }
            
            # Log search results for debugging
            for i, result in enumerate(search_results[:2]):
                logger.info(f"Search result {i+1}: {result['source']} (similarity: {result['similarity']:.3f})")
                logger.info(f"Content preview: {result['content'][:100]}...")
            
            # Step 3: Use RAG to reason over the retrieved information
            decision_result = await self._make_decision(query, structured_info, search_results)
            logger.info(f"Decision result: {decision_result.get('decision', 'N/A')}")
            
            return decision_result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "decision": "Uncertain",
                "amount": None,
                "justification": [{
                    "clause": "N/A", 
                    "text": f"Error processing query: {str(e)}", 
                    "source": "N/A"
                }],
                "alternatives": []
            }
    
    async def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured information"""
        try:
            system_prompt = """
            Extract structured information from the user's query about insurance.
            Return ONLY a valid JSON object with these fields:
            {
                "age": number or null,
                "procedure": "string" or null,
                "location": "string" or null,
                "policy_duration": "string" or null,
                "condition": "string" or null,
                "amount_requested": "string" or null
            }
            
            Do not include any explanation, just the JSON.
            """
            
            prompt = f"{system_prompt}\n\nQuery: {query}\n\nJSON:"
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean the response text
                response_text = response.text.strip()
                
                # Remove markdown formatting
                response_text = re.sub(r'```json\s*', '', response_text)
                response_text = re.sub(r'```\s*$', '', response_text)
                
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group()
                
                structured_info = json.loads(response_text)
                return structured_info
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse structured info as JSON: {e}")
                logger.warning(f"Raw response: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return {}
    
    async def _make_decision(
        self, 
        original_query: str, 
        structured_info: Dict[str, Any], 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Make a decision based on the query and retrieved documents"""
        try:
            # Prepare context from search results
            context_parts = []
            for i, result in enumerate(search_results):
                context_parts.append(
                    f"Document {i+1}:\n"
                    f"Source: {result['source']}\n"
                    f"Page: {result['page']}\n"
                    f"Content: {result['content']}\n"
                    f"Similarity: {result['similarity']:.3f}\n"
                )
            
            context = "\n".join(context_parts)
            
            system_prompt = """
            {
  "role": "system",
  "content": "You are an expert insurance claim processor. Analyze the query against all provided policy documents (PDFs) and extract every relevant piece of information you can find.\n\nRules:\n1. **Decision**: Must be one of \"Approved\", \"Rejected\", or \"Uncertain\".\n2. **Amount**: If a payout amount is explicitly specified, extract it as \"₹XX,XXX\"; otherwise use \"\".\n3. **Justification**: An array of citation objects, each with:\n   - **source**: filename (e.g. \"policy.pdf\");\n   - **clause**: location (e.g. \"Page 5, Section 2.1\");\n   - **text**: the quoted supporting text (max ~200 characters).\n4. **Details**: An array of any other relevant facts, definitions, limits, or exclusions you find, with the same citation object structure.\n5. **Alternatives**: If **decision** is \"Uncertain\", list follow‑up questions or missing data as citation‑style objects (same shape as justification):\n   - **source**: set to an empty string \"\";\n   - **clause**: set to an empty string \"\";\n   - **text**: the question or missing info.\n   Otherwise, use an empty array.\n6. **JSON Only**: Return exactly one valid JSON object—no prose, no markdown.\n\nFinal JSON schema:\n```\n{\n  \"decision\":   \"Approved\" | \"Rejected\" | \"Uncertain\",\n  \"amount\":     \"₹XX,XXX\" | \"\",\n  \"justification\": [\n    {\"source\":\"policy.pdf\",\"clause\":\"Page X, Section Y.Z\",\"text\":\"Quoted text supporting the decision.\"}\n  ],\n  \"details\": [\n    {\"source\":\"policy.pdf\",\"clause\":\"Page A, Section B.C\",\"text\":\"Additional relevant fact or exclusion.\"}\n  ],\n  \"alternatives\": [\n    {\"source\":\"\",\"clause\":\"\",\"text\":\"Is the insured’s age below 60?\"}\n  ]\n}\n When you  do not find exact answer form pdf, provide a summary of what you got from the pdf pertaining to the query```"
}

            """
            
            user_prompt = f"""
            Query: {original_query}
            
            Extracted Info: {json.dumps(structured_info)}
            
            Policy Documents:
            {context}
            
            Analyze and return JSON decision:
            """
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(full_prompt)
            
            try:
                # Clean the response text
                response_text = response.text.strip()
                
                # Remove markdown formatting
                response_text = re.sub(r'```json\s*', '', response_text)
                response_text = re.sub(r'```\s*$', '', response_text)
                
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group()
                
                decision_result = json.loads(response_text)
                
                # Validate the response structure
                if not isinstance(decision_result, dict):
                    raise ValueError("Response is not a dictionary")
                
                # Ensure required fields exist
                if "decision" not in decision_result:
                    decision_result["decision"] = "Uncertain"
                
                if "justification" not in decision_result or not isinstance(decision_result["justification"], list):
                    # Create justification from the first search result
                    if search_results:
                        best_result = search_results[0]
                        decision_result["justification"] = [{
                            "clause": f"Page {best_result['page']}",
                            "text": best_result['content'][:200] + "...",
                            "source": best_result['source']
                        }]
                    else:
                        decision_result["justification"] = [{
                            "clause": "N/A",
                            "text": "No relevant information found",
                            "source": "N/A"
                        }]
                
                if "alternatives" not in decision_result:
                    decision_result["alternatives"] = []
                
                return decision_result
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing decision result: {e}")
                logger.error(f"Raw response: {response.text}")
                
                # Create a manual decision based on search results
                if search_results:
                    best_result = search_results[0]
                    
                    # Simple keyword-based decision
                    content_lower = best_result['content'].lower()
                    query_lower = original_query.lower()
                    
                    decision = "Uncertain"
                    if any(word in content_lower for word in ["covered", "approved", "eligible"]):
                        if any(word in content_lower for word in ["waiting", "period", "days"]):
                            decision = "Uncertain"  # Needs more analysis
                        else:
                            decision = "Approved"
                    elif any(word in content_lower for word in ["excluded", "not covered", "rejected"]):
                        decision = "Rejected"
                    
                    # Extract amount if present
                    amount_match = re.search(r'₹[\d,]+', best_result['content'])
                    amount = amount_match.group() if amount_match else None
                    
                    return {
                        "decision": decision,
                        "amount": amount,
                        "justification": [{
                            "clause": f"Page {best_result['page']}",
                            "text": best_result['content'][:200] + "...",
                            "source": best_result['source']
                        }],
                        "alternatives": []
                    }
                else:
                    return {
                        "decision": "Uncertain",
                        "amount": None,
                        "justification": [{
                            "clause": "N/A",
                            "text": "Unable to process the policy documents properly.",
                            "source": "N/A"
                        }],
                        "alternatives": []
                    }
                
        except Exception as e:
            logger.error(f"Error making decision: {e}", exc_info=True)
            
            # Fallback response
            return {
                "decision": "Uncertain",
                "amount": None,
                "justification": [{
                    "clause": "N/A",
                    "text": f"Processing error: {str(e)}",
                    "source": "N/A"
                }],
                "alternatives": []
            }
