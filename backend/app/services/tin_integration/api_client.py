"""
TIN API Client for Knowledge Graph Extraction

This module provides an API client for interacting with the TIN Node Communications API
to extract data for knowledge graph generation. It follows the API-first principle,
using only the TIN API endpoints as the source of truth.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
import os

logger = logging.getLogger(__name__)


@dataclass
class TinApiConfig:
    """Configuration for TIN API client"""
    base_url: str
    jwt_token: str
    timeout: int = 30
    verify_ssl: bool = True


class TinApiClient:
    """
    Client for interacting with TIN Node Communications API.
    
    This client provides methods to retrieve data needed for knowledge graph
    extraction using only the official TIN API endpoints.
    """
    
    def __init__(self, config: TinApiConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.jwt_token}',
            'Content-Type': 'application/json'
        })
        self.session.verify = config.verify_ssl
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to TIN API"""
        url = urljoin(self.config.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {e}")
            raise
    
    def get_threads(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get thread overviews from /api/v3/threads/
        
        Returns thread metadata including root message info, participant counts,
        and basic thread statistics.
        """
        return self._make_request(
            'GET', 
            '/api/v3/threads/',
            params={'limit': limit, 'offset': offset}
        )
    
    def get_thread_messages(self, thread_id: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all messages in a specific thread from /api/v3/threads/{thread_id}/messages
        
        Returns messages in chronological order with full thread context.
        """
        return self._make_request(
            'GET',
            f'/api/v3/threads/{thread_id}/messages',
            params={'limit': limit, 'offset': offset}
        )
    
    def get_messages(self, 
                    originator_did: Optional[str] = None,
                    message_type: Optional[str] = None,
                    text_contains: Optional[str] = None,
                    root_uuid: Optional[str] = None,
                    limit: int = 1000, 
                    offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get messages with optional filters from /api/v3/messages
        
        Supports filtering by originator, type, content, and thread.
        """
        params = {'limit': limit, 'offset': offset}
        if originator_did:
            params['originator_did'] = originator_did
        if message_type:
            params['message_type'] = message_type
        if text_contains:
            params['text_contains'] = text_contains
        if root_uuid:
            params['root_uuid'] = root_uuid
            
        return self._make_request('GET', '/api/v3/messages', params=params)
    
    def get_message_by_uuid(self, message_uuid: str) -> Dict[str, Any]:
        """Get a specific message by UUID from /api/v3/messages/{message_uuid}"""
        return self._make_request('GET', f'/api/v3/messages/{message_uuid}')
    
    def get_message_applause(self, message_uuid: str) -> List[Dict[str, Any]]:
        """Get applause for a specific message from /api/v3/messages/{message_uuid}/applause"""
        return self._make_request('GET', f'/api/v3/messages/{message_uuid}/applause')
    
    def get_actors(self, 
                  type_name: Optional[str] = None,
                  limit: int = 500, 
                  offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get actors from /api/v3/actors/
        
        Supports filtering by actor type (e.g., 'human', 'ai_agent').
        """
        params = {'limit': limit, 'offset': offset}
        if type_name:
            params['type_name'] = type_name
            
        return self._make_request('GET', '/api/v3/actors/', params=params)
    
    def get_actor_by_did(self, actor_did: str) -> Dict[str, Any]:
        """Get specific actor by DID from /api/v3/actors/{actor_did}"""
        return self._make_request('GET', f'/api/v3/actors/{actor_did}')
    
    def get_actor_reputation(self, actor_did: str) -> Dict[str, Any]:
        """
        Get actor reputation factors from /api/v3/actors/{actor_did}/reputation
        
        Returns reputation factors including impact, consistency, and experience.
        """
        return self._make_request('GET', f'/api/v3/actors/{actor_did}/reputation')
    
    def get_actor_applause(self, actor_did: str) -> List[Dict[str, Any]]:
        """
        Get actor applause metrics from /api/v3/actors/{actor_did}/applause
        
        Returns aggregated applause metrics by content type.
        """
        return self._make_request('GET', f'/api/v3/actors/{actor_did}/applause')
    
    def get_knowledge_items(self,
                           originator_did: Optional[str] = None,
                           source_type: Optional[str] = None,
                           text_contains: Optional[str] = None,
                           limit: int = 1000,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get knowledge items from /api/v3/knowledge
        
        Supports filtering by originator, source type, and content.
        """
        params = {'limit': limit, 'offset': offset}
        if originator_did:
            params['originator_did'] = originator_did
        if source_type:
            params['source_type'] = source_type
        if text_contains:
            params['text_contains'] = text_contains
            
        return self._make_request('GET', '/api/v3/knowledge', params=params)
    
    def get_knowledge_item_by_uuid(self, knowledge_item_uuid: str) -> Dict[str, Any]:
        """Get specific knowledge item by UUID from /api/v3/knowledge/{knowledge_item_uuid}"""
        return self._make_request('GET', f'/api/v3/knowledge/{knowledge_item_uuid}')
    
    def create_knowledge_item(self, content: str, 
                             type_id_source: int,
                             source_ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new knowledge item via /api/v3/knowledge
        
        For knowledge graph results, this will typically be:
        - content: JSON serialized knowledge graph
        - type_id_source: ID for 'tin.knowledge.knowledge_graph' type
        - source_ref: Optional reference to source thread/message
        """
        payload = {
            'content': content,
            'type_id_source': type_id_source
        }
        if source_ref:
            payload['source_ref'] = source_ref
            
        return self._make_request('POST', '/api/v3/knowledge', json=payload)
    
    def get_reference_data(self, data_type: str) -> List[Dict[str, Any]]:
        """
        Get reference data from /api/v3/reference-data/{data_type}
        
        Supported types: message_types, actor_types, knowledge_source_types, etc.
        """
        return self._make_request('GET', f'/api/v3/reference-data/{data_type}')


def create_api_client_from_env() -> TinApiClient:
    """
    Create TIN API client from environment variables.
    
    Expected environment variables:
    - TIN_API_BASE_URL: Base URL for TIN API (e.g., http://localhost:8300)
    - TIN_API_JWT_TOKEN: JWT Bearer token for authentication
    - TIN_API_TIMEOUT: Request timeout in seconds (optional, default: 30)
    - TIN_API_VERIFY_SSL: Whether to verify SSL certificates (optional, default: true)
    """
    base_url = os.getenv('TIN_API_BASE_URL')
    jwt_token = os.getenv('TIN_API_JWT_TOKEN')
    
    if not base_url:
        raise ValueError("TIN_API_BASE_URL environment variable is required")
    if not jwt_token:
        raise ValueError("TIN_API_JWT_TOKEN environment variable is required")
    
    config = TinApiConfig(
        base_url=base_url,
        jwt_token=jwt_token,
        timeout=int(os.getenv('TIN_API_TIMEOUT', '30')),
        verify_ssl=os.getenv('TIN_API_VERIFY_SSL', 'true').lower() == 'true'
    )
    
    return TinApiClient(config)
