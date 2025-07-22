"""
TinGraphStore - Main implementation of the TIN knowledge graph

This module builds on the TripleStore to provide TIN-specific knowledge graph
functionality, including extraction from TIN database and concept handling.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, asdict
import networkx as nx
from collections import defaultdict, Counter
from .api_client import TinApiClient, create_api_client_from_env
from .triple_store import TripleStore


class TinGraphStore:
    """
    A TIN-specific knowledge graph implementation
    
    This class builds on the TripleStore to provide TIN-specific functionality
    for extracting knowledge from TIN databases and handling TIN concepts.
    """
    
    def __init__(self, 
                api_client: Optional[TinApiClient] = None,
                graph_db_path: Optional[Union[str, Path]] = None,
                create_if_missing: bool = True):
        """
        Initialize the TIN graph store with API-first approach
        
        Args:
            api_client: TIN API client for data access (if None, creates from env)
            graph_db_path: Path to the graph database (will be created if missing)
            create_if_missing: Create the graph database if it doesn't exist
        """
        # Initialize API client
        if api_client is None:
            self.api_client = create_api_client_from_env()
        else:
            self.api_client = api_client
        
        # Set up graph database path
        if graph_db_path is None:
            self.graph_db_path = Path("tin_knowledge_graph.db")
        else:
            self.graph_db_path = Path(graph_db_path)
        
        # Initialize the triple store
        self.triple_store = TripleStore(self.graph_db_path, create_if_missing)
        
        # Track statistics
        self._stats = {
            "thread_relations": 0,
            "actor_relations": 0,
            "concept_relations": 0,
            "last_extraction": None
        }
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def extract_thread_relationships(self, limit: Optional[int] = None) -> int:
        """
        Extract thread relationships using TIN API
        
        This extracts basic parent-child relationships between messages
        and links messages to their authors using the TIN API endpoints.
        
        Args:
            limit: Maximum number of messages to process (None = all)
            
        Returns:
            Number of relationships extracted
        """
        self.logger.info("Extracting thread relationships via TIN API...")
        
        relation_count = 0
        processed_messages = 0
        
        try:
            # Get all threads first to understand the structure
            threads = self.api_client.get_threads(limit=1000 if limit is None else limit)
            self.logger.info(f"Found {len(threads)} threads")
            
            for thread in threads:
                if limit and processed_messages >= limit:
                    break
                    
                # Get all messages in this thread
                thread_id = thread.get('root_uuid')
                if not thread_id:
                    continue
                    
                try:
                    messages = self.api_client.get_thread_messages(thread_id)
                    
                    # Process each message in the thread
                    for msg in messages:
                        if limit and processed_messages >= limit:
                            break
                            
                        # Add message as entity
                        message_uuid = msg.get('message_uuid')
                        if not message_uuid:
                            continue
                            
                        message_key = f"message:{message_uuid}"
                        content = msg.get('text', '') or msg.get('content', '')
                        content_preview = content[:100] + '...' if content and len(content) > 100 else content
                        
                        self.triple_store.add_entity(
                            entity_type="message",
                            value=message_uuid,
                            metadata={
                                "content_preview": content_preview,
                                "created_at": msg.get('created_at'),
                                "applause_count": msg.get('applause_count', 0),
                                "thread_id": thread_id,
                                "thread_position": msg.get('thread_position')
                            }
                        )
                        
                        # Add thread relationship if parent exists
                        parent_uuid = msg.get('related_message_uuid')
                        if parent_uuid:
                            parent_key = f"message:{parent_uuid}"
                            
                            self.triple_store.add_triple(
                                subject=message_key,
                                predicate="replies_to",
                                obj=parent_key,
                                source_type="message",
                                source_id=message_uuid
                            )
                            relation_count += 1
                        
                        # Add actor-message relationship
                        actor_did = msg.get('originator_did')
                        if actor_did:
                            actor_key = f"actor:{actor_did}"
                            
                            # Ensure actor entity exists
                            self.triple_store.add_entity(
                                entity_type="actor",
                                value=actor_did
                            )
                            
                            self.triple_store.add_triple(
                                subject=actor_key,
                                predicate="authored",
                                obj=message_key,
                                source_type="message",
                                source_id=message_uuid
                            )
                            relation_count += 1
                        
                        processed_messages += 1
                        
                except Exception as e:
                    self.logger.error(f"Error processing thread {thread_id}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error extracting thread relationships: {e}")
            return 0
        
        # Update statistics
        self._stats["thread_relations"] = relation_count
        self._stats["last_extraction"] = datetime.now().isoformat()
        
        self.logger.info(f"Extracted {relation_count} thread relationships from {processed_messages} messages")
        return relation_count
    
    def extract_actor_relationships(self, limit: Optional[int] = None) -> int:
        """
        Extract actor relationships using TIN API
        
        This extracts actor metadata and relationships between actors,
        including reputation/applause data from the authoritative TIN API.
        
        Args:
            limit: Maximum number of actors to process (None = all)
            
        Returns:
            Number of relationships extracted
        """
        self.logger.info("Extracting actor relationships via TIN API...")
        
        relation_count = 0
        processed_actors = 0
        
        try:
            # Get all actors from the API
            actors = self.api_client.get_actors(limit=limit or 1000)
            self.logger.info(f"Found {len(actors)} actors")
            
            for actor in actors:
                if limit and processed_actors >= limit:
                    break
                    
                actor_did = actor.get('actor_did')
                if not actor_did:
                    continue
                    
                actor_key = f"actor:{actor_did}"
                
                # Add actor entity with basic metadata
                self.triple_store.add_entity(
                    entity_type="actor",
                    value=actor_did,
                    metadata={
                        "display_name": actor.get('display_name'),
                        "type_id": actor.get('type_id'),
                        "type_name": actor.get('type_name'),
                        "created_at": actor.get('created_at'),
                        "avatar_url": actor.get('avatar_url')
                    }
                )
                
                # Add actor type relationship
                type_name = actor.get('type_name')
                if type_name:
                    type_key = f"actor_type:{type_name}"
                    
                    # Ensure type entity exists
                    self.triple_store.add_entity(
                        entity_type="actor_type",
                        value=type_name
                    )
                    
                    self.triple_store.add_triple(
                        subject=actor_key,
                        predicate="has_type",
                        obj=type_key,
                        source_type="actor",
                        source_id=actor_did
                    )
                    relation_count += 1
                
                # Get reputation data from TIN API (authoritative source)
                try:
                    reputation = self.api_client.get_actor_reputation(actor_did)
                    
                    # Add reputation relationships
                    for factor, value in reputation.items():
                        if isinstance(value, (int, float)) and value > 0:
                            reputation_key = f"reputation:{factor}"
                            
                            # Ensure reputation factor entity exists
                            self.triple_store.add_entity(
                                entity_type="reputation_factor",
                                value=factor
                            )
                            
                            self.triple_store.add_triple(
                                subject=actor_key,
                                predicate="has_reputation",
                                obj=reputation_key,
                                source_type="actor",
                                source_id=actor_did,
                                metadata={"value": value}
                            )
                            relation_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Could not get reputation for actor {actor_did}: {e}")
                
                # Get applause metrics from TIN API
                try:
                    applause_metrics = self.api_client.get_actor_applause(actor_did)
                    
                    for metric in applause_metrics:
                        content_type = metric.get('content_type')
                        applause_count = metric.get('applause_count', 0)
                        
                        if content_type and applause_count > 0:
                            applause_key = f"applause:{content_type}"
                            
                            # Ensure applause type entity exists
                            self.triple_store.add_entity(
                                entity_type="applause_type",
                                value=content_type
                            )
                            
                            self.triple_store.add_triple(
                                subject=actor_key,
                                predicate="received_applause",
                                obj=applause_key,
                                source_type="actor",
                                source_id=actor_did,
                                metadata={"count": applause_count}
                            )
                            relation_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Could not get applause for actor {actor_did}: {e}")
                
                processed_actors += 1
                
        except Exception as e:
            self.logger.error(f"Error extracting actor relationships: {e}")
            return 0
        
        # Update statistics
        self._stats["actor_relations"] = relation_count
        self._stats["last_extraction"] = datetime.now().isoformat()
        
        self.logger.info(f"Extracted {relation_count} actor relationships from {processed_actors} actors")
        return relation_count
    
    def extract_concepts_from_messages(self, 
                                      min_applause: int = 0,
                                      limit: Optional[int] = None,
                                      use_llm: bool = False,
                                      llm_service: Any = None) -> int:
        """
        Extract concepts from message content
        
        This uses simple keyword extraction or optional LLM analysis
        to identify concepts in messages.
        
        Args:
            min_applause: Minimum applause count for messages to analyze
            limit: Maximum number of messages to process (None = all)
            use_llm: Whether to use LLM for extraction
            llm_service: LLM service to use (must be provided if use_llm=True)
            
        Returns:
            Number of concept relationships extracted
        """
        print(f"Extracting concepts from messages in {self.tin_db_path}...")
        
        if use_llm and not llm_service:
            print("Warning: LLM service not provided, falling back to keyword extraction")
            use_llm = False
        
        # Connect to TIN database
        try:
            tin_conn = sqlite3.connect(self.tin_db_path)
            tin_conn.row_factory = sqlite3.Row
            tin_cur = tin_conn.cursor()
        except Exception as e:
            print(f"Error connecting to TIN database: {e}")
            return 0
        
        # Get messages with applause using the view
        query = '''
        SELECT message_uuid, text as content, applause_count
        FROM v_message_with_thread_context
        WHERE text IS NOT NULL AND length(text) > 10
        AND applause_count >= ?
        ORDER BY applause_count DESC
        '''
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            tin_cur.execute(query, (min_applause,))
            messages = tin_cur.fetchall()
        except Exception as e:
            print(f"Error querying messages: {e}")
            tin_conn.close()
            return 0
        
        relation_count = 0
        
        if use_llm:
            # LLM-based concept extraction (would integrate with your LLM service)
            # This is a placeholder - replace with your actual LLM integration
            pass
        else:
            # Simple keyword-based concept extraction
            # In a real implementation, this would be more sophisticated
            keywords = {
                "ai": "technology",
                "agent": "technology",
                "learning": "technology",
                "model": "technology",
                "data": "technology",
                "database": "technology",
                "user": "person",
                "neural": "technology",
                "llm": "technology",
                "language model": "technology",
                "architecture": "concept",
                "design": "concept",
                "security": "concept",
                "memory": "concept",
                "knowledge": "concept",
                "graph": "concept",
                "node": "concept",
                "relationship": "concept",
                "triple": "concept",
                "query": "concept",
                "search": "action",
                "find": "action",
                "create": "action",
                "update": "action",
                "delete": "action",
                "system": "concept",
                "tin": "system",
                "transparent information network": "system"
            }
            
            # Process messages for concepts
            for msg in messages:
                content = msg['content'].lower() if msg['content'] else ""
                message_uuid = msg['message_uuid']
                message_key = f"message:{message_uuid}"
                
                # Look for keywords in content
                for keyword, concept_type in keywords.items():
                    if keyword in content:
                        concept_key = f"concept:{keyword}"
                        
                        # Add concept entity
                        self.triple_store.add_entity(
                            entity_type="concept",
                            value=keyword,
                            metadata={"type": concept_type},
                            first_seen_in=message_uuid
                        )
                        
                        # Add message-concept relationship
                        self.triple_store.add_triple(
                            subject=message_key,
                            predicate="mentions",
                            obj=concept_key,
                            confidence=min(msg['applause_count'] / 5.0, 1.0),  # Higher applause = higher confidence
                            source_type="message",
                            source_id=message_uuid
                        )
                        relation_count += 1
        
        tin_conn.close()
        
        # Update statistics
        self._stats["concept_relations"] = relation_count
        self._stats["last_extraction"] = datetime.datetime.now().isoformat()
        
        print(f"Extracted {relation_count} concept relationships")
        return relation_count
    
    def query_related_concepts(self, concept: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find concepts related to the given concept
        
        Args:
            concept: Concept name to find related concepts for
            limit: Maximum number of related concepts to return
            
        Returns:
            List of related concepts with relationship information
        """
        concept_key = f"concept:{concept}"
        
        # Get messages that mention this concept
        concept_messages = self.triple_store.get_triples(
            predicate="mentions", 
            obj=concept_key
        )
        
        message_ids = [triple["subject"] for triple in concept_messages]
        
        # Find other concepts mentioned in those messages
        related_concepts = {}
        
        for message_id in message_ids:
            other_concepts = self.triple_store.get_triples(
                subject=message_id,
                predicate="mentions"
            )
            
            for triple in other_concepts:
                related_concept = triple["object"]
                if related_concept != concept_key:
                    if related_concept not in related_concepts:
                        related_concepts[related_concept] = {
                            "concept": related_concept.split(':', 1)[1],
                            "co_occurrences": 1,
                            "confidence": triple["confidence"]
                        }
                    else:
                        related_concepts[related_concept]["co_occurrences"] += 1
                        related_concepts[related_concept]["confidence"] = max(
                            related_concepts[related_concept]["confidence"],
                            triple["confidence"]
                        )
        
        # Sort by co-occurrences and return top results
        sorted_results = sorted(
            related_concepts.values(),
            key=lambda x: x["co_occurrences"],
            reverse=True
        )[:limit]
        
        return sorted_results
    
    def get_concept_path(self, start_concept: str, end_concept: str) -> List[Dict[str, Any]]:
        """
        Find a path between two concepts through messages
        
        Args:
            start_concept: Starting concept name
            end_concept: Ending concept name
            
        Returns:
            List of nodes in the path, or empty list if no path exists
        """
        start_key = f"concept:{start_concept}"
        end_key = f"concept:{end_concept}"
        
        # Get messages that mention the start concept
        start_messages = self.triple_store.get_triples(
            predicate="mentions",
            obj=start_key
        )
        
        # Get messages that mention the end concept
        end_messages = self.triple_store.get_triples(
            predicate="mentions",
            obj=end_key
        )
        
        # Check for direct connection (same message mentions both)
        start_message_ids = {triple["subject"] for triple in start_messages}
        end_message_ids = {triple["subject"] for triple in end_messages}
        
        direct_connections = start_message_ids.intersection(end_message_ids)
        if direct_connections:
            # Direct connection exists
            message_id = list(direct_connections)[0]
            return [
                {"type": "concept", "id": start_key, "value": start_concept},
                {"type": "message", "id": message_id},
                {"type": "concept", "id": end_key, "value": end_concept}
            ]
        
        # TODO: Implement more complex path finding
        # This would require graph traversal algorithms
        # For now, we'll just return an empty list
        return []
    
    def get_actor_knowledge_map(self, actor_did: str, limit: int = 50) -> Dict[str, Any]:
        """
        Generate a knowledge map for an actor
        
        This shows what concepts an actor has discussed in their messages.
        
        Args:
            actor_did: Actor DID to create knowledge map for
            limit: Maximum number of concepts to include
            
        Returns:
            Dictionary with actor information and related concepts
        """
        actor_key = f"actor:{actor_did}"
        
        # Get messages authored by this actor
        actor_messages = self.triple_store.get_triples(
            subject=actor_key,
            predicate="authored"
        )
        
        message_ids = [triple["object"] for triple in actor_messages]
        
        # Find concepts mentioned in those messages
        concept_counts = {}
        
        for message_id in message_ids:
            concepts = self.triple_store.get_triples(
                subject=message_id,
                predicate="mentions"
            )
            
            for triple in concepts:
                concept_key = triple["object"]
                concept = concept_key.split(':', 1)[1]
                
                if concept not in concept_counts:
                    concept_counts[concept] = {
                        "count": 1,
                        "confidence": triple["confidence"],
                        "messages": [message_id]
                    }
                else:
                    concept_counts[concept]["count"] += 1
                    concept_counts[concept]["confidence"] = max(
                        concept_counts[concept]["confidence"],
                        triple["confidence"]
                    )
                    concept_counts[concept]["messages"].append(message_id)
        
        # Sort by count and limit results
        top_concepts = sorted(
            [{"concept": k, **v} for k, v in concept_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:limit]
        
        return {
            "actor_did": actor_did,
            "message_count": len(message_ids),
            "concept_count": len(concept_counts),
            "top_concepts": top_concepts
        }
    
    def export_json(self, output_path: Union[str, Path], max_nodes: int = 500) -> Dict[str, Any]:
        """
        Export the graph to JSON format for visualization
        
        Args:
            output_path: Path to write the JSON file
            max_nodes: Maximum number of nodes to include
            
        Returns:
            Dictionary with export statistics
        """
        print(f"Exporting graph to {output_path}...")
        
        # Connect to graph database
        conn = sqlite3.connect(self.graph_db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get nodes (entities)
        cur.execute('''
        SELECT e.id, e.type, e.value, e.metadata,
            (SELECT COUNT(*) FROM triples WHERE subject LIKE (e.type || ':' || e.value || '%')) as outgoing,
            (SELECT COUNT(*) FROM triples WHERE object LIKE (e.type || ':' || e.value || '%')) as incoming
        FROM entities e
        ORDER BY (outgoing + incoming) DESC
        LIMIT ?
        ''', (max_nodes,))
        
        entities = cur.fetchall()
        
        # Build nodes list
        nodes = []
        node_ids = set()
        
        for entity in entities:
            entity_key = f"{entity['type']}:{entity['value']}"
            node_ids.add(entity_key)
            
            node = {
                "id": entity_key,
                "type": entity['type'],
                "value": entity['value'],
                "connections": entity['outgoing'] + entity['incoming']
            }
            
            if entity['metadata']:
                try:
                    metadata = json.loads(entity['metadata'])
                    node.update(metadata)
                except:
                    pass
            
            nodes.append(node)
        
        # Get edges between included nodes
        edges = []
        
        for node_id in node_ids:
            # Get outgoing connections
            cur.execute('''
            SELECT subject, predicate, object, confidence
            FROM triples
            WHERE subject = ?
            ''', (node_id,))
            
            for row in cur.fetchall():
                if row['object'] in node_ids:
                    edges.append({
                        "source": row['subject'],
                        "target": row['object'],
                        "relationship": row['predicate'],
                        "confidence": row['confidence']
                    })
        
        conn.close()
        
        # Create JSON structure
        graph_data = {
            "nodes": nodes,
            "edges": edges,
            "stats": self._stats,
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "edge_count": len(edges),
                "api_base_url": self.api_client.config.base_url,
                "graph_db": str(self.graph_db_path)
            }
        }
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"Exported {len(nodes)} nodes and {len(edges)} edges")
        
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "output_path": str(output_path)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the graph store
        
        Returns:
            Dictionary with statistics
        """
        triple_stats = self.triple_store.get_statistics()
        
        stats = {
            **triple_stats,
            **self._stats,
            "graph_db_path": str(self.graph_db_path),
            "api_base_url": self.api_client.config.base_url
        }
        
        return stats
    
    def create_knowledge_graph_item(self, 
                                   thread_id: Optional[str] = None,
                                   source_ref: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a knowledge graph knowledge item via TIN API
        
        This method extracts the current knowledge graph state and creates
        a knowledge item of type 'tin.knowledge.knowledge_graph' via the TIN API.
        This enables the asynchronous, event-driven knowledge graph generation
        pattern where KG agents reply to threads with knowledge graph analysis.
        
        Args:
            thread_id: Optional thread ID to associate with the knowledge graph
            source_ref: Optional source reference for the knowledge graph
            
        Returns:
            Created knowledge item data, or None if creation failed
        """
        try:
            # Get reference data to find the knowledge_graph source type ID
            source_types = self.api_client.get_reference_data('knowledge_source_types')
            kg_type = next(
                (t for t in source_types if t.get('source_type') == 'tin.knowledge.knowledge_graph'),
                None
            )
            
            if not kg_type:
                self.logger.error("Could not find 'tin.knowledge.knowledge_graph' source type")
                return None
            
            # Export current graph state to JSON
            graph_stats = self.get_statistics()
            
            # Create a comprehensive knowledge graph representation
            kg_data = {
                "extraction_timestamp": datetime.now().isoformat(),
                "statistics": graph_stats,
                "thread_id": thread_id,
                "entities": self._get_entity_summary(),
                "relationships": self._get_relationship_summary(),
                "top_actors": self._get_top_actors(),
                "top_concepts": self._get_top_concepts(),
                "metadata": {
                    "extractor": "TinGraphStore",
                    "version": "2.0-api",
                    "extraction_method": "api_based"
                }
            }
            
            # Serialize to JSON
            kg_json = json.dumps(kg_data, indent=2)
            
            # Create knowledge item via API
            result = self.api_client.create_knowledge_item(
                content=kg_json,
                type_id_source=kg_type['type_id'],
                source_ref=source_ref or thread_id
            )
            
            self.logger.info(f"Created knowledge graph knowledge item: {result.get('knowledge_item_uuid')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create knowledge graph knowledge item: {e}")
            return None

    def create_thread_summary_message(self, 
                                    thread_id: str,
                                    summary_text: str,
                                    originator_agent: str = "TinGraphStore",
                                    include_kg_analysis: bool = True) -> Optional[Dict[str, Any]]:
        """
        Create a thread summary message that complements the knowledge graph
        
        This implements the unified thread intelligence model where each thread gets:
        1. Knowledge graph (semantic structure) - created as knowledge item
        2. Narrative summary (human interpretation) - created as message
        
        Args:
            thread_id: Thread to summarize
            summary_text: Human-readable summary text
            originator_agent: Name of the agent creating the summary
            include_kg_analysis: Whether to include KG statistics in the summary
            
        Returns:
            Created message data, or None if creation failed
        """
        try:
            # Get message types to find tin.system.summary
            message_types = self.api_client.get_reference_data('message_types')
            summary_type = next(
                (t for t in message_types if t.get('type_name') == 'tin.system.summary'),
                None
            )
            
            if not summary_type:
                self.logger.error("Could not find 'tin.system.summary' message type")
                return None
            
            # Prepare summary content
            summary_content = {
                "text": summary_text,
                "originator_agent": originator_agent
            }
            
            # Optionally include KG analysis
            if include_kg_analysis:
                stats = self.get_statistics()
                summary_content["knowledge_graph_analysis"] = {
                    "entities_extracted": stats.get("total_entities", 0),
                    "relationships_extracted": stats.get("total_relationships", 0),
                    "top_concepts": self._get_top_concepts()[:5],  # Top 5 concepts
                    "extraction_timestamp": datetime.now().isoformat()
                }
            
            # Create the summary message
            result = self.api_client.create_message(
                thread_id=thread_id,
                content=json.dumps(summary_content, indent=2),
                message_type_id=summary_type['type_id']
            )
            
            self.logger.info(f"Created thread summary message: {result.get('message_uuid')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create thread summary message: {e}")
            return None
    
    def _get_entity_summary(self) -> Dict[str, int]:
        """Get summary of entities by type"""
        try:
            conn = self.triple_store.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
            SELECT type, COUNT(*) as count
            FROM entities
            GROUP BY type
            ORDER BY count DESC
            ''')
            
            return {row[0]: row[1] for row in cur.fetchall()}
        except Exception as e:
            self.logger.warning(f"Could not get entity summary: {e}")
            return {}
    
    def _get_relationship_summary(self) -> Dict[str, int]:
        """Get summary of relationships by predicate"""
        try:
            conn = self.triple_store.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
            SELECT predicate, COUNT(*) as count
            FROM triples
            GROUP BY predicate
            ORDER BY count DESC
            ''')
            
            return {row[0]: row[1] for row in cur.fetchall()}
        except Exception as e:
            self.logger.warning(f"Could not get relationship summary: {e}")
            return {}
    
    def _get_top_actors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top actors by connection count"""
        try:
            conn = self.triple_store.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
            SELECT e.value, e.metadata,
                   COUNT(t.subject) + COUNT(t2.object) as connections
            FROM entities e
            LEFT JOIN triples t ON t.subject = ('actor:' || e.value)
            LEFT JOIN triples t2 ON t2.object = ('actor:' || e.value)
            WHERE e.type = 'actor'
            GROUP BY e.value, e.metadata
            ORDER BY connections DESC
            LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cur.fetchall():
                actor_data = {
                    "actor_did": row[0],
                    "connections": row[2]
                }
                
                if row[1]:  # metadata
                    try:
                        metadata = json.loads(row[1])
                        actor_data.update(metadata)
                    except:
                        pass
                        
                results.append(actor_data)
            
            return results
        except Exception as e:
            self.logger.warning(f"Could not get top actors: {e}")
            return []
    
    def _get_top_concepts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top concepts by mention count"""
        try:
            conn = self.triple_store.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
            SELECT e.value, COUNT(t.object) as mentions
            FROM entities e
            LEFT JOIN triples t ON t.object = ('concept:' || e.value)
            WHERE e.type = 'concept'
            GROUP BY e.value
            ORDER BY mentions DESC
            LIMIT ?
            ''', (limit,))
            
            return [
                {"concept": row[0], "mentions": row[1]}
                for row in cur.fetchall()
            ]
        except Exception as e:
            self.logger.warning(f"Could not get top concepts: {e}")
            return []
