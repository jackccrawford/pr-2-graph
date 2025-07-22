"""
TripleStore - Core implementation of a lightweight SQLite-based triple store

This module implements a simple, append-only triple store that forms the 
foundation of the TIN knowledge graph without external dependencies.
"""

import sqlite3
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set, Iterator


class TripleStore:
    """
    A lightweight, append-only triple store backed by SQLite
    
    This class implements the core Subject-Predicate-Object storage
    that forms the foundation of the knowledge graph. It follows
    TIN's immutability principles with an insert-only pattern.
    """
    
    def __init__(self, db_path: Path, create_if_missing: bool = True):
        """
        Initialize the triple store with a SQLite database
        
        Args:
            db_path: Path to the SQLite database file
            create_if_missing: Create the database if it doesn't exist
        """
        self.db_path = db_path
        
        if create_if_missing:
            self.db_path.parent.mkdir(exist_ok=True)
            self._setup_schema()
    
    def _setup_schema(self) -> None:
        """Set up the SQLite schema for the triple store"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Create triple store table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS triples (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            source_type TEXT,
            source_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subject, predicate, object) ON CONFLICT IGNORE
        )
        ''')
        
        # Create concept table for entity metadata
        cur.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            metadata TEXT,  -- JSON metadata
            first_seen_in TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(type, value) ON CONFLICT IGNORE
        )
        ''')
        
        # Create indexes for faster queries
        cur.execute('CREATE INDEX IF NOT EXISTS idx_subject ON triples(subject)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_object ON triples(object)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_predicate ON triples(predicate)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_entity_value ON entities(value)')
        
        conn.commit()
        conn.close()
    
    def add_triple(self, 
                  subject: str, 
                  predicate: str, 
                  obj: str,
                  confidence: float = 1.0,
                  source_type: Optional[str] = None,
                  source_id: Optional[str] = None) -> str:
        """
        Add a triple to the store
        
        Args:
            subject: Subject of the triple
            predicate: Predicate (relationship)
            obj: Object of the triple
            confidence: Confidence score (0.0-1.0)
            source_type: Type of the source (e.g., 'message', 'actor')
            source_id: ID of the source entity
            
        Returns:
            ID of the created triple
        """
        triple_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''
        INSERT INTO triples (id, subject, predicate, object, confidence, source_type, source_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (triple_id, subject, predicate, obj, confidence, source_type, source_id))
        
        conn.commit()
        conn.close()
        
        return triple_id
    
    def add_entity(self, 
                  entity_type: str, 
                  value: str, 
                  metadata: Optional[Dict[str, Any]] = None,
                  first_seen_in: Optional[str] = None) -> str:
        """
        Add an entity to the store
        
        Args:
            entity_type: Type of entity (e.g., 'actor', 'message', 'concept')
            value: Value/name of the entity
            metadata: Additional metadata as a dictionary
            first_seen_in: ID of the source where this entity was first seen
            
        Returns:
            ID of the created entity
        """
        entity_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata) if metadata else None
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''
        INSERT INTO entities (id, type, value, metadata, first_seen_in)
        VALUES (?, ?, ?, ?, ?)
        ''', (entity_id, entity_type, value, metadata_json, first_seen_in))
        
        conn.commit()
        conn.close()
        
        return entity_id
    
    def get_triples(self, 
                   subject: Optional[str] = None, 
                   predicate: Optional[str] = None, 
                   obj: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get triples matching the given criteria
        
        Args:
            subject: Filter by subject (optional)
            predicate: Filter by predicate (optional)
            obj: Filter by object (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching triples as dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        query = "SELECT * FROM triples WHERE 1=1"
        params = []
        
        if subject is not None:
            query += " AND subject = ?"
            params.append(subject)
        
        if predicate is not None:
            query += " AND predicate = ?"
            params.append(predicate)
        
        if obj is not None:
            query += " AND object = ?"
            params.append(obj)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_entity(self, entity_type: str, value: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity by type and value
        
        Args:
            entity_type: Type of the entity
            value: Value/name of the entity
            
        Returns:
            Entity as a dictionary, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('''
        SELECT * FROM entities
        WHERE type = ? AND value = ?
        ''', (entity_type, value))
        
        row = cur.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            return result
        
        return None
    
    def get_entities_by_type(self, entity_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all entities of a specific type
        
        Args:
            entity_type: Type of entities to retrieve
            limit: Maximum number of results
            
        Returns:
            List of entities as dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('''
        SELECT * FROM entities
        WHERE type = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (entity_type, limit))
        
        rows = cur.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            results.append(result)
        
        return results
    
    def search_entities(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search entities by value
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching entities as dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('''
        SELECT * FROM entities
        WHERE value LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (f'%{query}%', limit))
        
        rows = cur.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            results.append(result)
        
        return results
    
    def get_entity_connections(self, entity_type: str, value: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get connections for an entity
        
        This retrieves both incoming and outgoing connections for the entity,
        with optional recursive depth.
        
        Args:
            entity_type: Type of the entity
            value: Value/name of the entity
            depth: Depth of connections (1 = direct connections only)
            
        Returns:
            Dictionary with incoming and outgoing connections
        """
        entity_key = f"{entity_type}:{value}"
        
        # Get outgoing connections (entity is subject)
        outgoing = self.get_triples(subject=entity_key)
        
        # Get incoming connections (entity is object)
        incoming = self.get_triples(obj=entity_key)
        
        result = {
            "entity": entity_key,
            "outgoing": outgoing,
            "incoming": incoming
        }
        
        # If depth > 1, recursively get connections for connected entities
        if depth > 1:
            next_entities = set()
            
            # Add connected entities from outgoing connections
            for triple in outgoing:
                next_entities.add((triple['object'].split(':', 1)[0], triple['object'].split(':', 1)[1]))
            
            # Add connected entities from incoming connections
            for triple in incoming:
                next_entities.add((triple['subject'].split(':', 1)[0], triple['subject'].split(':', 1)[1]))
            
            # Get connections for each connected entity
            result['next_level'] = {}
            for next_type, next_value in next_entities:
                if f"{next_type}:{next_value}" != entity_key:  # Avoid cycles
                    result['next_level'][f"{next_type}:{next_value}"] = self.get_entity_connections(
                        next_type, next_value, depth - 1
                    )
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the triple store
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Count triples
        cur.execute("SELECT COUNT(*) FROM triples")
        triple_count = cur.fetchone()[0]
        
        # Count entities
        cur.execute("SELECT COUNT(*) FROM entities")
        entity_count = cur.fetchone()[0]
        
        # Count entity types
        cur.execute('''
        SELECT type, COUNT(*) as count
        FROM entities
        GROUP BY type
        ORDER BY count DESC
        ''')
        entity_types = {row[0]: row[1] for row in cur.fetchall()}
        
        # Count predicates
        cur.execute('''
        SELECT predicate, COUNT(*) as count
        FROM triples
        GROUP BY predicate
        ORDER BY count DESC
        ''')
        predicates = {row[0]: row[1] for row in cur.fetchall()}
        
        conn.close()
        
        return {
            "triple_count": triple_count,
            "entity_count": entity_count,
            "entity_types": entity_types,
            "predicates": predicates,
            "db_path": str(self.db_path)
        }
