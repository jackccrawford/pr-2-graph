"""
Enhanced GraphService with TIN Node Graph Integration

This service extends the original GraphService to support persistent storage
while maintaining full backward compatibility.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.graph import (
    KnowledgeGraph, GraphNode, GraphEdge, GraphTriplet,
    PRConversation, PRComment, GraphAnalysis
)
from .llm_service import ollama_service
from .tin_integration import PRGraphAdapter


class EnhancedGraphService:
    """Enhanced GraphService with TIN Node Graph persistent storage"""
    
    def __init__(self, use_persistent_storage: bool = True):
        # Backward compatibility: maintain in-memory storage alongside persistent storage
        self.analyses: Dict[str, GraphAnalysis] = {}
        self.use_persistent_storage = use_persistent_storage
        self.logger = logging.getLogger(__name__)
        
        # Initialize TIN Node Graph adapter if persistent storage is enabled
        if self.use_persistent_storage:
            try:
                self.pr_adapter = PRGraphAdapter()
                self.logger.info("TIN Node Graph persistent storage initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize persistent storage: {e}. Falling back to in-memory only.")
                self.use_persistent_storage = False
                self.pr_adapter = None
        else:
            self.pr_adapter = None
    
    async def create_analysis(self, conversation: PRConversation) -> str:
        """Create a new graph analysis with persistent storage"""
        analysis_id = str(uuid.uuid4())
        
        knowledge_graph = await self._extract_knowledge_graph(conversation)
        
        # Create GraphAnalysis compatible with the expected model structure
        analysis = GraphAnalysis(
            analysis_id=analysis_id,
            conversation=conversation,
            knowledge_graph=knowledge_graph,
            created_at=datetime.utcnow(),
            statistics=self._calculate_statistics(knowledge_graph)
        )
        
        # Store in memory for backward compatibility
        self.analyses[analysis_id] = analysis
        
        # Store persistently if enabled
        if self.use_persistent_storage and self.pr_adapter:
            try:
                # Create a compatible object for the PR adapter
                adapter_analysis = type('GraphAnalysis', (), {
                    'id': analysis_id,
                    'nodes': knowledge_graph.nodes,
                    'relationships': knowledge_graph.triplets,
                    'metadata': {
                        "conversation": {
                            "pr_number": getattr(conversation, 'pr_number', None),
                            "repository": getattr(conversation, 'repository', None),
                            "title": getattr(conversation, 'title', None)
                        },
                        "statistics": self._calculate_statistics(knowledge_graph),
                        "extraction_method": "semantic_analysis"
                    },
                    'created_at': datetime.utcnow().isoformat()
                })()
                
                persistent_id = self.pr_adapter.store_graph_analysis(adapter_analysis)
                self.logger.info(f"Analysis {analysis_id} stored persistently as {persistent_id}")
            except Exception as e:
                self.logger.error(f"Failed to store analysis persistently: {e}")
        
        return analysis_id
    
    def get_analysis(self, analysis_id: str) -> Optional[GraphAnalysis]:
        """Get analysis by ID from memory or persistent storage"""
        # First check in-memory storage
        if analysis_id in self.analyses:
            return self.analyses[analysis_id]
        
        # If not in memory and persistent storage is enabled, try to retrieve from storage
        if self.use_persistent_storage and self.pr_adapter:
            try:
                # Try with analysis_ prefix for persistent storage format
                persistent_id = f"analysis_{analysis_id}" if not analysis_id.startswith("analysis_") else analysis_id
                analysis = self.pr_adapter.retrieve_graph_analysis(persistent_id)
                if analysis:
                    # Cache in memory for future access
                    self.analyses[analysis_id] = analysis
                    self.logger.info(f"Retrieved analysis {analysis_id} from persistent storage")
                    return analysis
            except Exception as e:
                self.logger.error(f"Failed to retrieve analysis from persistent storage: {e}")
        
        return None
    
    def list_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all analyses with metadata"""
        analyses = []
        
        # Add in-memory analyses
        for analysis_id, analysis in list(self.analyses.items())[:limit]:
            analyses.append({
                "analysis_id": analysis_id,
                "title": getattr(analysis.conversation, 'title', 'Untitled Analysis'),
                "created_at": analysis.created_at,
                "node_count": len(analysis.knowledge_graph.nodes),
                "relationship_count": len(analysis.knowledge_graph.triplets),
                "source": "memory"
            })
        
        # Add persistent analyses if available
        if self.use_persistent_storage and self.pr_adapter:
            try:
                persistent_analyses = self.pr_adapter.list_analyses(limit - len(analyses))
                for p_analysis in persistent_analyses:
                    # Avoid duplicates
                    if not any(a["analysis_id"] == p_analysis["analysis_id"] for a in analyses):
                        p_analysis["source"] = "persistent"
                        analyses.append(p_analysis)
            except Exception as e:
                self.logger.error(f"Failed to list persistent analyses: {e}")
        
        return analyses[:limit]
    
    def export_for_visualization(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Export analysis for D3.js and Flutter visualization"""
        if self.use_persistent_storage and self.pr_adapter:
            try:
                persistent_id = f"analysis_{analysis_id}" if not analysis_id.startswith("analysis_") else analysis_id
                viz_data = self.pr_adapter.export_for_visualization(persistent_id)
                if viz_data:
                    return viz_data
            except Exception as e:
                self.logger.error(f"Failed to export from persistent storage: {e}")
        
        # Fallback to in-memory analysis
        analysis = self.get_analysis(analysis_id)
        if analysis:
            return {
                "nodes": [
                    {
                        "id": node.id,
                        "label": node.label,
                        "type": node.type,
                        "properties": node.properties
                    }
                    for node in analysis.knowledge_graph.nodes
                ],
                "links": [
                    {
                        "source": rel.subject,
                        "target": rel.object,
                        "relationship": rel.predicate,
                        "properties": rel.metadata
                    }
                    for rel in analysis.knowledge_graph.triplets
                ],
                "metadata": {
                    "analysis_id": analysis_id,
                    "created_at": analysis.created_at,
                    "node_count": len(analysis.knowledge_graph.nodes),
                    "relationship_count": len(analysis.knowledge_graph.triplets)
                }
            }
        
        return None
    
    # All the original methods remain the same for backward compatibility
    async def _extract_knowledge_graph(self, conversation: PRConversation) -> KnowledgeGraph:
        """Extract knowledge graph from PR conversation"""
        nodes = []
        edges = []
        triplets = []
        
        participants = self._identify_participants(conversation.comments)
        for participant_id, participant_info in participants.items():
            nodes.append(GraphNode(
                id=participant_id,
                label=participant_info["display_name"],
                type="participant",
                properties={
                    "role": participant_info["role"],
                    "comment_count": participant_info["comment_count"]
                }
            ))
        
        issues = self._extract_issues(conversation.comments)
        for issue_id, issue_info in issues.items():
            nodes.append(GraphNode(
                id=issue_id,
                label=issue_info["title"],
                type="issue",
                properties=issue_info
            ))
        
        solutions = self._extract_solutions(conversation.comments)
        for solution_id, solution_info in solutions.items():
            nodes.append(GraphNode(
                id=solution_id,
                label=solution_info["title"],
                type="solution",
                properties=solution_info
            ))
        
        relationships = await self._extract_relationships(conversation.comments, participants, issues, solutions)
        
        node_ids = {node.id for node in nodes}
        
        valid_relationships = []
        for rel in relationships:
            if rel['source'] in node_ids and rel['target'] in node_ids:
                valid_relationships.append(rel)
        
        for rel in valid_relationships:
            edge_id = f"{rel['source']}-{rel['relationship']}-{rel['target']}"
            edges.append(GraphEdge(
                id=edge_id,
                source=rel["source"],
                target=rel["target"],
                relationship=rel["relationship"],
                properties=rel.get("metadata", {})
            ))
            
            triplets.append(GraphTriplet(
                subject=rel["source"],
                predicate=rel["relationship"],
                object=rel["target"],
                properties=rel.get("metadata", {})
            ))
        
        return KnowledgeGraph(
            nodes=nodes,
            edges=edges,
            triplets=triplets,
            metadata={
                "extraction_method": "semantic_analysis",
                "participant_count": len(participants),
                "issue_count": len(issues),
                "solution_count": len(solutions)
            }
        )
    
    def _identify_participants(self, comments: List[PRComment]) -> Dict[str, Dict[str, Any]]:
        """Identify participants and their roles"""
        participants = {}
        
        for comment in comments:
            author = comment.author
            if author not in participants:
                participants[author] = {
                    "display_name": author,
                    "role": "contributor",
                    "comment_count": 0,
                    "first_comment": comment.created_at,
                    "expertise": []
                }
            
            participants[author]["comment_count"] += 1
            
            # Determine role based on comment patterns
            body_lower = comment.body.lower()
            if any(keyword in body_lower for keyword in ["implements", "fix", "solution", "resolves"]):
                participants[author]["role"] = "implementer"
            elif any(keyword in body_lower for keyword in ["analyzes", "root cause", "investigation"]):
                participants[author]["role"] = "analyst"
            elif any(keyword in body_lower for keyword in ["coordinates", "guidance", "strategy"]):
                participants[author]["role"] = "coordinator"
        
        return participants
    
    def _extract_issues(self, comments: List[PRComment]) -> Dict[str, Dict[str, Any]]:
        """Extract technical issues from comments"""
        issues = {}
        issue_counter = 1
        
        for comment in comments:
            body_lower = comment.body.lower()
            
            # Look for issue indicators
            if any(keyword in body_lower for keyword in ["error", "bug", "issue", "problem", "fails", "broken"]):
                issue_id = f"issue_{issue_counter}"
                
                # Extract key phrases for the issue
                sentences = comment.body.split('.')
                issue_sentences = [s.strip() for s in sentences if any(kw in s.lower() for kw in ["error", "bug", "issue", "problem", "fails", "broken"])]
                
                if issue_sentences:
                    issues[issue_id] = {
                        "title": issue_sentences[0][:100] + "..." if len(issue_sentences[0]) > 100 else issue_sentences[0],
                        "description": " ".join(issue_sentences),
                        "author": comment.author,
                        "comment_id": comment.id,
                        "severity": "high" if any(kw in body_lower for kw in ["critical", "urgent", "blocking"]) else "medium",
                        "keywords": ["error", "bug", "issue", "problem"]
                    }
                    issue_counter += 1
        
        return issues
    
    def _extract_solutions(self, comments: List[PRComment]) -> Dict[str, Dict[str, Any]]:
        """Extract solutions from comments"""
        solutions = {}
        solution_counter = 1
        
        for comment in comments:
            body_lower = comment.body.lower()
            
            # Look for solution indicators
            if any(keyword in body_lower for keyword in ["fix", "solution", "resolve", "implement", "patch"]):
                solution_id = f"solution_{solution_counter}"
                
                # Extract key phrases for the solution
                sentences = comment.body.split('.')
                solution_sentences = [s.strip() for s in sentences if any(kw in s.lower() for kw in ["fix", "solution", "resolve", "implement", "patch"])]
                
                if solution_sentences:
                    solutions[solution_id] = {
                        "title": solution_sentences[0][:100] + "..." if len(solution_sentences[0]) > 100 else solution_sentences[0],
                        "description": " ".join(solution_sentences),
                        "author": comment.author,
                        "comment_id": comment.id,
                        "complexity": "high" if any(kw in body_lower for kw in ["complex", "refactor", "overhaul"]) else "medium",
                        "keywords": ["fix", "solution", "resolve", "implement"]
                    }
                    solution_counter += 1
        
        return solutions
    
    async def _extract_relationships(self, comments: List[PRComment], participants: Dict, issues: Dict, solutions: Dict) -> List[Dict[str, Any]]:
        """Extract relationships between entities using LLM analysis"""
        relationships = []
        
        for comment in comments:
            try:
                # Try LLM analysis first
                analysis_result = await ollama_service.analyze_comment_relationships(
                    comment.body,
                    list(participants.keys()),
                    list(issues.keys()),
                    list(solutions.keys())
                )
                
                if analysis_result and "relationships" in analysis_result:
                    for rel in analysis_result["relationships"]:
                        relationships.append({
                            "source": rel["source"],
                            "relationship": rel["relationship"],
                            "target": rel["target"],
                            "confidence": rel.get("confidence", 0.8),
                            "metadata": {
                                "comment_id": comment.id,
                                "extraction_method": "llm_analysis"
                            }
                        })
            except Exception as e:
                # Fallback to keyword-based extraction
                self.logger.warning(f"LLM analysis failed for comment {comment.id}: {e}")
                relationships.extend(self._fallback_keyword_extraction(comment, issues, solutions))
        
        # Add temporal relationships
        for i, comment in enumerate(comments[1:], 1):
            prev_comment = comments[i-1]
            if comment.author != prev_comment.author:
                relationships.append({
                    "source": comment.author,
                    "relationship": "REPLIES_TO", 
                    "target": prev_comment.author,
                    "confidence": 1.0,
                    "metadata": {"temporal_sequence": i, "comment_id": comment.id}
                })
        
        return relationships
    
    def _fallback_keyword_extraction(self, comment: PRComment, issues: Dict, solutions: Dict) -> List[Dict[str, Any]]:
        """Fallback keyword-based extraction when LLM is unavailable"""
        relationships = []
        author = comment.author
        body_lower = comment.body.lower()
        
        if "analyzes" in body_lower or "analysis" in body_lower or "root cause" in body_lower:
            for issue_id in issues.keys():
                if any(keyword in body_lower for keyword in issues[issue_id]["keywords"]):
                    relationships.append({
                        "source": author,
                        "relationship": "ANALYZES",
                        "target": issue_id,
                        "confidence": 0.7,
                        "metadata": {"comment_id": comment.id, "extraction_method": "fallback_keywords"}
                    })
        
        if "implements" in body_lower or "fix applied" in body_lower or "implementing" in body_lower:
            for solution_id in solutions.keys():
                if any(keyword in body_lower for keyword in solutions[solution_id]["keywords"]):
                    relationships.append({
                        "source": author,
                        "relationship": "IMPLEMENTS",
                        "target": solution_id,
                        "confidence": 0.8,
                        "metadata": {"comment_id": comment.id, "extraction_method": "fallback_keywords"}
                    })
        
        return relationships
    
    def _calculate_statistics(self, graph: KnowledgeGraph) -> Dict[str, Any]:
        """Calculate statistics for the knowledge graph"""
        return {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "triplet_count": len(graph.triplets),
            "node_types": list(set(node.type for node in graph.nodes)),
            "relationship_types": list(set(edge.relationship for edge in graph.edges)),
            "avg_confidence": 0.8  # Default confidence for backward compatibility
        }


# Create enhanced service instance
enhanced_graph_service = EnhancedGraphService()
