"""
PR Graph Adapter - Bridge between pr-2-graph and TIN Node Graph

This adapter converts pr-2-graph GraphTriplet objects to TIN Node Graph
Subject-Predicate-Object triples and provides persistent storage.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict

from ...models.graph import GraphTriplet, GraphNode, GraphAnalysis
from .triple_store import TripleStore
from .graph_store import TinGraphStore


class PRGraphAdapter:
    """
    Adapter that bridges pr-2-graph knowledge graphs with TIN Node Graph persistence
    """
    
    def __init__(self, 
                 graph_db_path: Optional[Union[str, Path]] = None,
                 create_if_missing: bool = True):
        """
        Initialize the PR graph adapter
        
        Args:
            graph_db_path: Path to the SQLite database (defaults to pr_knowledge_graph.db)
            create_if_missing: Create database if it doesn't exist
        """
        if graph_db_path is None:
            graph_db_path = Path("pr_knowledge_graph.db")
        else:
            graph_db_path = Path(graph_db_path)
        
        # Initialize TIN Node Graph store (without API client for local use)
        self.tin_store = TinGraphStore(
            api_client=None,  # We'll use local storage only
            graph_db_path=graph_db_path,
            create_if_missing=create_if_missing
        )
        
        self.logger = logging.getLogger(__name__)
    
    def store_graph_analysis(self, analysis: GraphAnalysis) -> str:
        """
        Store a complete GraphAnalysis in the TIN Node Graph triple store
        
        Args:
            analysis: GraphAnalysis object from pr-2-graph
            
        Returns:
            Analysis ID for retrieval
        """
        analysis_id = f"analysis_{analysis.id}"
        
        try:
            # Store nodes as entities
            for node in analysis.nodes:
                self._store_node_as_entity(node, analysis_id)
            
            # Store relationships as triples
            for triplet in analysis.relationships:
                self._store_triplet_as_triple(triplet, analysis_id)
            
            # Store analysis metadata
            self._store_analysis_metadata(analysis, analysis_id)
            
            self.logger.info(f"Stored analysis {analysis_id} with {len(analysis.nodes)} nodes and {len(analysis.relationships)} relationships")
            return analysis_id
            
        except Exception as e:
            self.logger.error(f"Failed to store graph analysis: {e}")
            raise
    
    def retrieve_graph_analysis(self, analysis_id: str) -> Optional[GraphAnalysis]:
        """
        Retrieve a GraphAnalysis from the triple store
        
        Args:
            analysis_id: Analysis ID to retrieve
            
        Returns:
            GraphAnalysis object or None if not found
        """
        try:
            # Get analysis metadata
            metadata = self._get_analysis_metadata(analysis_id)
            if not metadata:
                return None
            
            # Reconstruct nodes and relationships
            nodes = self._reconstruct_nodes(analysis_id)
            relationships = self._reconstruct_relationships(analysis_id)
            
            # Create GraphAnalysis object
            analysis = GraphAnalysis(
                id=metadata.get('original_id', analysis_id),
                nodes=nodes,
                relationships=relationships,
                metadata=metadata.get('analysis_metadata', {}),
                created_at=metadata.get('created_at', datetime.utcnow().isoformat())
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve analysis {analysis_id}: {e}")
            return None
    
    def export_for_visualization(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Export analysis data in format compatible with D3.js and Flutter visualizations
        
        Args:
            analysis_id: Analysis ID to export
            
        Returns:
            Dictionary with nodes and links for visualization
        """
        try:
            analysis = self.retrieve_graph_analysis(analysis_id)
            if not analysis:
                return None
            
            # Convert to visualization format
            viz_data = {
                "nodes": [
                    {
                        "id": node.id,
                        "label": node.label,
                        "type": node.type,
                        "properties": node.properties,
                        "x": node.properties.get("x", 0),
                        "y": node.properties.get("y", 0)
                    }
                    for node in analysis.nodes
                ],
                "links": [
                    {
                        "source": rel.subject,
                        "target": rel.object,
                        "relationship": rel.predicate,
                        "properties": rel.properties
                    }
                    for rel in analysis.relationships
                ],
                "metadata": {
                    "analysis_id": analysis_id,
                    "created_at": analysis.created_at,
                    "node_count": len(analysis.nodes),
                    "relationship_count": len(analysis.relationships)
                }
            }
            
            return viz_data
            
        except Exception as e:
            self.logger.error(f"Failed to export visualization data: {e}")
            return None
    
    def list_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all stored analyses with metadata
        
        Args:
            limit: Maximum number of analyses to return
            
        Returns:
            List of analysis summaries
        """
        try:
            # Query the triple store for analysis entities
            conn = self.tin_store.triple_store.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
            SELECT DISTINCT subject, metadata
            FROM entities 
            WHERE type = 'analysis' 
            ORDER BY created_at DESC 
            LIMIT ?
            ''', (limit,))
            
            analyses = []
            for row in cur.fetchall():
                analysis_id = row[0]
                try:
                    metadata = json.loads(row[1]) if row[1] else {}
                    analyses.append({
                        "analysis_id": analysis_id,
                        "title": metadata.get("title", "Untitled Analysis"),
                        "created_at": metadata.get("created_at"),
                        "node_count": metadata.get("node_count", 0),
                        "relationship_count": metadata.get("relationship_count", 0)
                    })
                except json.JSONDecodeError:
                    continue
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Failed to list analyses: {e}")
            return []
    
    def _store_node_as_entity(self, node: GraphNode, analysis_id: str):
        """Store a GraphNode as a TIN entity"""
        entity_key = f"{analysis_id}:node:{node.id}"
        
        # Store the node as an entity
        self.tin_store.triple_store.add_entity(
            entity_key,
            node.type,
            json.dumps({
                "label": node.label,
                "properties": node.properties,
                "analysis_id": analysis_id
            })
        )
        
        # Add relationship to analysis
        self.tin_store.triple_store.add_triple(
            analysis_id,
            "contains_node",
            entity_key
        )
    
    def _store_triplet_as_triple(self, triplet: GraphTriplet, analysis_id: str):
        """Store a GraphTriplet as a TIN triple"""
        subject_key = f"{analysis_id}:node:{triplet.subject}"
        object_key = f"{analysis_id}:node:{triplet.object}"
        
        # Store the relationship
        self.tin_store.triple_store.add_triple(
            subject_key,
            triplet.predicate,
            object_key,
            json.dumps(triplet.properties) if triplet.properties else None
        )
        
        # Add relationship to analysis
        self.tin_store.triple_store.add_triple(
            analysis_id,
            "contains_relationship",
            f"{subject_key}:{triplet.predicate}:{object_key}"
        )
    
    def _store_analysis_metadata(self, analysis: GraphAnalysis, analysis_id: str):
        """Store analysis metadata as an entity"""
        metadata = {
            "original_id": analysis.id,
            "created_at": analysis.created_at,
            "node_count": len(analysis.nodes),
            "relationship_count": len(analysis.relationships),
            "analysis_metadata": analysis.metadata
        }
        
        self.tin_store.triple_store.add_entity(
            analysis_id,
            "analysis",
            json.dumps(metadata)
        )
    
    def _get_analysis_metadata(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis metadata"""
        try:
            conn = self.tin_store.triple_store.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
            SELECT metadata FROM entities 
            WHERE value = ? AND type = 'analysis'
            ''', (analysis_id,))
            
            row = cur.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata for {analysis_id}: {e}")
            return None
    
    def _reconstruct_nodes(self, analysis_id: str) -> List[GraphNode]:
        """Reconstruct GraphNode objects from stored entities"""
        try:
            conn = self.tin_store.triple_store.get_connection()
            cur = conn.cursor()
            
            # Get all nodes for this analysis
            cur.execute('''
            SELECT e.value, e.type, e.metadata
            FROM entities e
            JOIN triples t ON t.object = e.value
            WHERE t.subject = ? AND t.predicate = 'contains_node'
            ''', (analysis_id,))
            
            nodes = []
            for row in cur.fetchall():
                entity_key = row[0]
                node_type = row[1]
                try:
                    metadata = json.loads(row[2]) if row[2] else {}
                    
                    # Extract node ID from entity key
                    node_id = entity_key.split(":")[-1]
                    
                    node = GraphNode(
                        id=node_id,
                        label=metadata.get("label", node_id),
                        type=node_type,
                        properties=metadata.get("properties", {})
                    )
                    nodes.append(node)
                    
                except json.JSONDecodeError:
                    continue
            
            return nodes
            
        except Exception as e:
            self.logger.error(f"Failed to reconstruct nodes: {e}")
            return []
    
    def _reconstruct_relationships(self, analysis_id: str) -> List[GraphTriplet]:
        """Reconstruct GraphTriplet objects from stored triples"""
        try:
            conn = self.tin_store.triple_store.get_connection()
            cur = conn.cursor()
            
            # Get all relationships for this analysis
            cur.execute('''
            SELECT t.subject, t.predicate, t.object, t.metadata
            FROM triples t
            WHERE t.subject LIKE ? AND t.predicate != 'contains_node' AND t.predicate != 'contains_relationship'
            ''', (f"{analysis_id}:node:%",))
            
            relationships = []
            for row in cur.fetchall():
                subject_key = row[0]
                predicate = row[1]
                object_key = row[2]
                metadata = row[3]
                
                # Extract node IDs from keys
                subject_id = subject_key.split(":")[-1]
                object_id = object_key.split(":")[-1]
                
                try:
                    properties = json.loads(metadata) if metadata else {}
                except json.JSONDecodeError:
                    properties = {}
                
                triplet = GraphTriplet(
                    subject=subject_id,
                    predicate=predicate,
                    object=object_id,
                    properties=properties
                )
                relationships.append(triplet)
            
            return relationships
            
        except Exception as e:
            self.logger.error(f"Failed to reconstruct relationships: {e}")
            return []
