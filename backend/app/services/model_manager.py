"""Smart model manager with memory optimization and Ollama lifecycle control."""

import asyncio
import subprocess
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import httpx
from ..config.settings import settings, get_model_config, get_memory_config, get_ollama_config
from ..config.prompts import ANALYSIS_SYSTEM_PROMPTS

logger = logging.getLogger(__name__)


class OllamaClient:
    """Async Ollama client with timeout and error handling."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.base_url = settings.ollama_base_url
        self.timeout = settings.ollama_timeout
        
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from model."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
                
            except httpx.TimeoutException:
                logger.error(f"Timeout calling model {self.model_name}")
                raise
            except Exception as e:
                logger.error(f"Error calling model {self.model_name}: {e}")
                raise


class SmartModelManager:
    """Memory-aware model manager with automatic lifecycle control."""
    
    def __init__(self):
        self.model_config = get_model_config()
        self.memory_config = get_memory_config()
        
        # Always loaded models
        self.primary = OllamaClient(self.model_config["primary"])
        self.critic = OllamaClient(self.model_config["critic"])
        self.embeddings = OllamaClient(self.model_config["embeddings"])
        self.formatter = OllamaClient(self.model_config["formatter"])
        
        # On-demand models
        self.fallback: Optional[OllamaClient] = None
        self.fallback_loaded = False
        
        # Usage tracking
        self.request_count = 0
        self.fallback_usage = 0
        self.last_cleanup = datetime.now()
        
        logger.info(f"Initialized SmartModelManager with models: {self.model_config}")
    
    async def analyze_pr_conversation(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PR conversation with critique workflow."""
        self.request_count += 1
        
        try:
            # Standard workflow with efficient models
            primary_analysis = await self._primary_analysis(pr_data)
            
            if settings.enable_critique:
                critique = await self._critic_review(pr_data, primary_analysis)
                
                if self._has_valid_suggestions(critique):
                    refined = await self._refine_analysis(primary_analysis, critique)
                    return refined
            
            return primary_analysis
            
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            logger.warning(f"Primary analysis failed: {e}, switching to fallback")
            self.fallback_usage += 1
            return await self._fallback_analysis(pr_data)
    
    async def _primary_analysis(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Primary analysis using configured model."""
        system_prompt = ANALYSIS_SYSTEM_PROMPTS["primary_analyzer"]
        conversation_text = self._format_pr_data(pr_data)
        
        response = await self.primary.generate(
            prompt=f"Analyze this PR conversation:\n\n{conversation_text}",
            system_prompt=system_prompt
        )
        
        # Parse response into structured format
        return self._parse_analysis_response(response)
    
    async def _critic_review(self, pr_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Critic review using configured model."""
        system_prompt = ANALYSIS_SYSTEM_PROMPTS["critic_reviewer"]
        conversation_text = self._format_pr_data(pr_data)
        analysis_text = str(analysis)
        
        response = await self.critic.generate(
            prompt=f"Review this analysis:\n\nOriginal conversation:\n{conversation_text}\n\nAnalysis:\n{analysis_text}",
            system_prompt=system_prompt
        )
        
        return self._parse_critique_response(response)
    
    async def _refine_analysis(self, original: Dict[str, Any], critique: Dict[str, Any]) -> Dict[str, Any]:
        """Refine analysis based on critic feedback."""
        system_prompt = """Refine the original analysis based on the critic's feedback.
        
        Keep what's accurate, fix what's wrong, add what's missing.
        Return the improved analysis in the same JSON format."""
        
        response = await self.primary.generate(
            prompt=f"Original analysis:\n{original}\n\nCritic feedback:\n{critique}\n\nProvide refined analysis:",
            system_prompt=system_prompt
        )
        
        return self._parse_analysis_response(response)
    
    async def _fallback_analysis(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis with memory management."""
        # Step 1: Stop primary model to free memory
        await self._stop_model(self.model_config["primary"])
        
        # Step 2: Load fallback model
        if not self.fallback_loaded:
            self.fallback = OllamaClient(self.model_config["fallback"])
            self.fallback_loaded = True
            logger.info(f"Loaded fallback model: {self.model_config['fallback']}")
            
            # Wait for model to load
            await asyncio.sleep(2)
        
        # Step 3: Analyze with fallback
        system_prompt = """You are an expert at analyzing GitHub PR conversations.
        
        Provide comprehensive analysis including relationships, breakthrough moments, 
        participant roles, and technical decisions. Return structured JSON."""
        
        conversation_text = self._format_pr_data(pr_data)
        
        if self.fallback is None:
            raise RuntimeError("Fallback model not properly initialized")
        
        response = await self.fallback.generate(
            prompt=f"Analyze this PR conversation:\n\n{conversation_text}",
            system_prompt=system_prompt
        )
        
        result = self._parse_analysis_response(response)
        
        # Step 4: Decide whether to cleanup
        if self.memory_config["auto_cleanup"]:
            await self._cleanup_fallback()
        
        return result
    
    async def _stop_model(self, model_name: str):
        """Stop Ollama model to free memory."""
        try:
            result = subprocess.run(
                ["ollama", "stop", model_name], 
                check=True, 
                capture_output=True, 
                timeout=10,
                text=True
            )
            logger.info(f"✅ Stopped model: {model_name}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Failed to stop model {model_name}: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.warning(f"⚠️ Timeout stopping model {model_name}")
        except FileNotFoundError:
            logger.warning("⚠️ Ollama CLI not found, cannot stop models")
    
    async def _cleanup_fallback(self):
        """Clean up fallback model and reload primary."""
        try:
            if self.fallback_loaded:
                await self._stop_model(self.model_config["fallback"])
                self.fallback = None
                self.fallback_loaded = False
            
            # Reinitialize primary (will load on first use)
            self.primary = OllamaClient(self.model_config["primary"])
            logger.info("✅ Cleaned up fallback, primary model ready")
            
        except Exception as e:
            logger.error(f"⚠️ Error during cleanup: {e}")
    
    def _format_pr_data(self, pr_data: Dict[str, Any]) -> str:
        """Format PR data for analysis."""
        # Simple formatting for now - can be enhanced
        if isinstance(pr_data, dict) and "conversation" in pr_data:
            return pr_data["conversation"]
        return str(pr_data)
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured analysis."""
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
                
                # Extract structured data from parsed JSON
                analysis_data = parsed_json.get('analysis', {})
                
                return {
                    "raw_response": response,
                    "relationships": self._extract_relationships(analysis_data),
                    "breakthrough_moments": analysis_data.get('breakthrough_moments', []),
                    "participants": self._extract_participants(analysis_data),
                    "technical_decisions": analysis_data.get('technical_decision_points', []),
                    "confidence": analysis_data.get('confidence', 0.7),
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from response: {e}")
        
        # Fallback: try to parse the entire response as JSON
        try:
            parsed_json = json.loads(response)
            return {
                "raw_response": response,
                "parsed_data": parsed_json,
                "relationships": [],
                "breakthrough_moments": [],
                "participants": {},
                "confidence": 0.6,
                "timestamp": datetime.now().isoformat()
            }
        except json.JSONDecodeError:
            # Final fallback: return raw response with basic structure
            return {
                "raw_response": response,
                "relationships": [],
                "breakthrough_moments": [],
                "participants": {},
                "confidence": 0.5,
                "timestamp": datetime.now().isoformat(),
                "parsing_error": "Could not extract structured data from response"
            }
    
    def _parse_critique_response(self, response: str) -> Dict[str, Any]:
        """Parse critic response."""
        return {
            "raw_feedback": response,
            "accuracy_concerns": [],
            "missing_elements": [],
            "confidence_adjustments": {},
            "has_suggestions": len(response.strip()) > 50  # Simple heuristic
        }
    
    def _has_valid_suggestions(self, critique: Dict[str, Any]) -> bool:
        """Check if critique has valid suggestions."""
        return critique.get("has_suggestions", False)
    
    def _extract_relationships(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships from analysis data."""
        relationships = []
        
        # Extract from key_relationships if present
        key_relationships = analysis_data.get('key_relationships', [])
        for rel in key_relationships:
            relationships.append({
                "source": rel.get('participant', 'unknown'),
                "target": "project",  # Default target
                "relationship_type": rel.get('role', 'CONTRIBUTES').upper(),
                "frequency": rel.get('frequency', 'unknown'),
                "notes": rel.get('notes', '')
            })
        
        return relationships
    
    def _extract_participants(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract participant information from analysis data."""
        participants = {}
        
        # Extract from participant_roles_and_contributions if present
        participant_data = analysis_data.get('participant_roles_and_contributions', [])
        for participant in participant_data:
            name = participant.get('participant', 'unknown')
            participants[name] = {
                "role": participant.get('role', 'contributor'),
                "contributions": participant.get('contributions', []),
                "activity_level": "active"  # Default
            }
        
        # Also extract from key_relationships
        key_relationships = analysis_data.get('key_relationships', [])
        for rel in key_relationships:
            name = rel.get('participant', 'unknown')
            if name not in participants:
                participants[name] = {
                    "role": rel.get('role', 'contributor'),
                    "contributions": [],
                    "activity_level": rel.get('frequency', 'unknown')
                }
        
        return participants
    
    async def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        return {
            "models": self.model_config,
            "memory_config": self.memory_config,
            "request_count": self.request_count,
            "fallback_usage": self.fallback_usage,
            "fallback_loaded": self.fallback_loaded,
            "fallback_rate": self.fallback_usage / max(self.request_count, 1),
            "last_cleanup": self.last_cleanup.isoformat()
        }
    
    async def cleanup(self):
        """Clean up all models."""
        models_to_stop = [
            self.model_config["primary"],
            self.model_config["fallback"],
            self.model_config["critic"]
        ]
        
        for model in models_to_stop:
            await self._stop_model(model)
        
        logger.info("✅ All models stopped")


# Global model manager instance
model_manager = SmartModelManager()
