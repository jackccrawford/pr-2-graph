import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class OllamaService:
    """Service for interacting with Ollama language models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate(self, model: str, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        """Generate response from Ollama model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1024
                }
            }
            
            if system:
                payload["system"] = system
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": result.get("model", model),
                "created_at": result.get("created_at"),
                "done": result.get("done", True)
            }
            
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "fallback_available": True
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error {e.response.status_code}: {e.response.text}",
                "fallback_available": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "fallback_available": False
            }
    
    async def analyze_participant_role(self, comment: Dict[str, Any], model: str = "llama3.2:1b") -> Dict[str, Any]:
        """Analyze participant role and contribution type"""
        from .config.prompts import PARTICIPANT_ANALYSIS_PROMPT
        
        prompt = PARTICIPANT_ANALYSIS_PROMPT.format(
            author=comment["author"],
            body=comment["body"][:1000],  # Limit context length
            created_at=comment["created_at"]
        )
        
        system = "You are an expert at analyzing collaborative conversations and identifying participant roles and contribution types. Respond with structured JSON only."
        
        result = await self.generate(model, prompt, system)
        
        if result["success"]:
            try:
                analysis = json.loads(result["response"])
                return {
                    "success": True,
                    "analysis": analysis,
                    "model_used": model
                }
            except json.JSONDecodeError:
                return self._fallback_participant_analysis(comment)
        else:
            return self._fallback_participant_analysis(comment)
    
    async def extract_relationships(self, entity1: Dict[str, Any], entity2: Dict[str, Any], context: str, model: str = "llama3.2:1b") -> Dict[str, Any]:
        """Extract semantic relationships between entities"""
        from .config.prompts import RELATIONSHIP_EXTRACTION_PROMPT
        
        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(
            entity1_type=entity1.get("type", "unknown"),
            entity1_label=entity1.get("label", "unknown"),
            entity2_type=entity2.get("type", "unknown"), 
            entity2_label=entity2.get("label", "unknown"),
            context=context[:800]  # Limit context length
        )
        
        system = "You are an expert at identifying semantic relationships in collaborative conversations. Focus on asymmetric patterns and nuanced insights. Respond with structured JSON only."
        
        result = await self.generate(model, prompt, system)
        
        if result["success"]:
            try:
                relationship = json.loads(result["response"])
                return {
                    "success": True,
                    "relationship": relationship,
                    "model_used": model
                }
            except json.JSONDecodeError:
                return self._fallback_relationship_extraction(entity1, entity2, context)
        else:
            return self._fallback_relationship_extraction(entity1, entity2, context)
    
    async def identify_breakthrough_moments(self, comments: List[Dict[str, Any]], model: str = "llama3.2:1b") -> Dict[str, Any]:
        """Identify breakthrough moments and insights in conversation"""
        from .config.prompts import BREAKTHROUGH_ANALYSIS_PROMPT
        
        conversation_text = "\n\n".join([
            f"[{comment['author']} at {comment['created_at']}]: {comment['body'][:500]}"
            for comment in comments[-10:]  # Last 10 comments for context
        ])
        
        prompt = BREAKTHROUGH_ANALYSIS_PROMPT.format(
            conversation=conversation_text
        )
        
        system = "You are an expert at identifying breakthrough moments, novel insights, and problem-solving patterns in collaborative conversations. Respond with structured JSON only."
        
        result = await self.generate(model, prompt, system)
        
        if result["success"]:
            try:
                breakthroughs = json.loads(result["response"])
                return {
                    "success": True,
                    "breakthroughs": breakthroughs,
                    "model_used": model
                }
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse breakthrough analysis"}
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}
    
    def _fallback_participant_analysis(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback keyword-based participant analysis"""
        author = comment["author"]
        body_lower = comment["body"].lower()
        
        if "devin-ai-integration" in author.lower():
            role = "implementation_specialist"
            contribution_type = "empirical_testing"
            expertise = "frontend_development"
        elif "cascade" in body_lower and author == "jackccrawford":
            role = "strategic_analyst"
            contribution_type = "root_cause_analysis"
            expertise = "backend_architecture"
        else:
            role = "coordinator"
            contribution_type = "process_orchestration"
            expertise = "project_management"
        
        return {
            "success": True,
            "analysis": {
                "role": role,
                "contribution_type": contribution_type,
                "expertise": expertise,
                "insight_novelty": 0.5,  # Default moderate novelty
                "confidence": 0.7
            },
            "model_used": "fallback_keywords"
        }
    
    def _fallback_relationship_extraction(self, entity1: Dict[str, Any], entity2: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Fallback keyword-based relationship extraction"""
        context_lower = context.lower()
        
        if "analyzes" in context_lower or "analysis" in context_lower:
            relationship = "ANALYZES"
            confidence = 0.7
        elif "implements" in context_lower or "implementing" in context_lower:
            relationship = "IMPLEMENTS"
            confidence = 0.8
        elif "provides" in context_lower or "guidance" in context_lower:
            relationship = "PROVIDES"
            confidence = 0.6
        else:
            relationship = "RELATES_TO"
            confidence = 0.5
        
        return {
            "success": True,
            "relationship": {
                "type": relationship,
                "confidence": confidence,
                "evidence": context[:200],
                "asymmetric": False  # Keyword matching can't detect asymmetry
            },
            "model_used": "fallback_keywords"
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


ollama_service = OllamaService()
