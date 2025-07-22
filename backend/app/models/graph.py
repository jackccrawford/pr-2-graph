from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class GraphNode(BaseModel):
    """Represents a node in the knowledge graph"""
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Represents an edge/relationship in the knowledge graph"""
    id: str
    source: str
    target: str
    relationship: str
    properties: Dict[str, Any] = {}


class GraphTriplet(BaseModel):
    """Represents a Subject-Predicate-Object triplet"""
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = {}


class KnowledgeGraph(BaseModel):
    """Complete knowledge graph representation"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    triplets: List[GraphTriplet]
    metadata: Dict[str, Any] = {}


class PRComment(BaseModel):
    """Represents a PR comment"""
    id: str
    author: str
    created_at: datetime
    body: str
    comment_type: str = "comment"  # comment, commit, review
    metadata: Dict[str, Any] = {}


class PRConversation(BaseModel):
    """Represents a complete PR conversation"""
    pr_number: int
    repository: str
    title: str
    description: str
    comments: List[PRComment]
    participants: List[str]
    created_at: datetime
    metadata: Dict[str, Any] = {}


class GraphAnalysis(BaseModel):
    """Analysis result containing knowledge graph"""
    analysis_id: str
    conversation: PRConversation
    knowledge_graph: KnowledgeGraph
    created_at: datetime
    statistics: Dict[str, Any] = {}
