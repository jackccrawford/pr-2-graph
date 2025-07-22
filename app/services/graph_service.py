import uuid
from typing import List, Dict, Any
from datetime import datetime
from app.models.graph import (
    KnowledgeGraph, GraphNode, GraphEdge, GraphTriplet,
    PRConversation, PRComment, GraphAnalysis
)
from app.services.llm_service import ollama_service


class GraphService:
    """Service for processing knowledge graphs"""
    
    def __init__(self):
        self.analyses: Dict[str, GraphAnalysis] = {}
    
    async def create_analysis(self, conversation: PRConversation) -> str:
        """Create a new graph analysis"""
        analysis_id = str(uuid.uuid4())
        
        knowledge_graph = await self._extract_knowledge_graph(conversation)
        
        analysis = GraphAnalysis(
            analysis_id=analysis_id,
            conversation=conversation,
            knowledge_graph=knowledge_graph,
            created_at=datetime.utcnow(),
            statistics=self._calculate_statistics(knowledge_graph)
        )
        
        self.analyses[analysis_id] = analysis
        return analysis_id
    
    def get_analysis(self, analysis_id: str) -> GraphAnalysis:
        """Get analysis by ID"""
        if analysis_id not in self.analyses:
            raise ValueError(f"Analysis '{analysis_id}' not found")
        return self.analyses[analysis_id]
    
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
                confidence=rel.get("confidence", 1.0),
                metadata=rel.get("metadata", {})
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
                role = "human"
                display_name = author
                
                if "devin-ai-integration" in author.lower():
                    role = "ai_flutter_specialist"
                    display_name = "Devin (AI Flutter Specialist)"
                elif "cascade" in comment.body.lower() and author == "jackccrawford":
                    role = "ai_backend_specialist"
                    display_name = "Cascade (AI Backend Specialist)"
                elif author == "jackccrawford" and "cascade" not in comment.body.lower():
                    role = "human"
                    display_name = "Jack (Human)"
                
                participants[author] = {
                    "display_name": display_name,
                    "role": role,
                    "comment_count": 0
                }
            
            participants[author]["comment_count"] += 1
        
        return participants
    
    def _extract_issues(self, comments: List[PRComment]) -> Dict[str, Dict[str, Any]]:
        """Extract technical issues from comments"""
        issues = {}
        
        issue_patterns = [
            ("authentication_issue", "Authentication Flow", ["403", "401", "authentication", "auth", "token"]),
            ("message_format_issue", "Message Format", ["500", "malformed", "payload", "json"]),
            ("duplication_issue", "Message Duplication", ["duplicate", "duplication", "twice"]),
            ("api_parsing_issue", "API Parsing", ["parsing", "field", "uuid", "message_uuid"]),
            ("debug_execution_issue", "Debug Execution", ["debug", "logs", "not executing"])
        ]
        
        for comment in comments:
            body_lower = comment.body.lower()
            for issue_id, issue_title, keywords in issue_patterns:
                if any(keyword in body_lower for keyword in keywords):
                    if issue_id not in issues:
                        issues[issue_id] = {
                            "title": issue_title,
                            "keywords": keywords,
                            "mentioned_by": [],
                            "first_mentioned": comment.created_at
                        }
                    issues[issue_id]["mentioned_by"].append(comment.author)
        
        return issues
    
    def _extract_solutions(self, comments: List[PRComment]) -> Dict[str, Dict[str, Any]]:
        """Extract solutions from comments"""
        solutions = {}
        
        solution_patterns = [
            ("message_format_fix", "Message Format Fix", ["jsonencode", "json.encode", "payload fix"]),
            ("api_parsing_fix", "API Parsing Fix", ["message_uuid", "field mapping", "fromtinv3json"]),
            ("authentication_fix", "Authentication Fix", ["auth fix", "token handling", "jwt"]),
            ("duplication_fix", "Duplication Fix", ["deduplication", "addmessagewithoutduplicates"])
        ]
        
        for comment in comments:
            body_lower = comment.body.lower()
            for solution_id, solution_title, keywords in solution_patterns:
                if any(keyword in body_lower for keyword in keywords):
                    if solution_id not in solutions:
                        solutions[solution_id] = {
                            "title": solution_title,
                            "keywords": keywords,
                            "proposed_by": [],
                            "first_proposed": comment.created_at
                        }
                    solutions[solution_id]["proposed_by"].append(comment.author)
        
        return solutions
    
    async def _extract_relationships(self, comments: List[PRComment], participants: Dict, issues: Dict, solutions: Dict) -> List[Dict[str, Any]]:
        """Extract relationships between entities using LLM analysis"""
        relationships = []
        
        comment_data = [{"author": c.author, "body": c.body, "created_at": c.created_at.isoformat()} for c in comments]
        breakthrough_result = await ollama_service.identify_breakthrough_moments(comment_data)
        
        breakthrough_nodes = []
        if breakthrough_result["success"]:
            breakthroughs = breakthrough_result["breakthroughs"]
            
            for breakthrough in breakthroughs.get("breakthrough_moments", []):
                breakthrough_id = breakthrough["moment_id"]
                breakthrough_nodes.append(breakthrough_id)
                relationships.append({
                    "source": breakthrough["participant"],
                    "relationship": "PROVIDES_BREAKTHROUGH",
                    "target": breakthrough_id,
                    "confidence": breakthrough["novelty"],
                    "metadata": {
                        "insight_type": breakthrough["insight_type"],
                        "evidence": breakthrough["evidence"],
                        "impact": breakthrough["impact"]
                    }
                })
        
        for comment in comments:
            author = comment.author
            comment_data = {"author": author, "body": comment.body, "created_at": comment.created_at.isoformat()}
            
            role_result = await ollama_service.analyze_participant_role(comment_data)
            if role_result["success"]:
                analysis = role_result["analysis"]
                
                if analysis["contribution_type"] == "root_cause_analysis":
                    for issue_id in issues.keys():
                        if any(keyword in comment.body.lower() for keyword in issues[issue_id]["keywords"]):
                            relationships.append({
                                "source": author,
                                "relationship": "DIAGNOSES_ROOT_CAUSE",
                                "target": issue_id,
                                "confidence": analysis["confidence"],
                                "metadata": {
                                    "comment_id": comment.id,
                                    "insight_novelty": analysis["insight_novelty"],
                                    "evidence": analysis.get("evidence", [])
                                }
                            })
                
                elif analysis["contribution_type"] == "empirical_testing":
                    for solution_id in solutions.keys():
                        if any(keyword in comment.body.lower() for keyword in solutions[solution_id]["keywords"]):
                            relationships.append({
                                "source": author,
                                "relationship": "CONFIRMS_THROUGH_TESTING",
                                "target": solution_id,
                                "confidence": analysis["confidence"],
                                "metadata": {
                                    "comment_id": comment.id,
                                    "technical_precision": analysis.get("technical_precision", 0.8)
                                }
                            })
                
                elif analysis["contribution_type"] == "systematic_validation":
                    relationships.append({
                        "source": author,
                        "relationship": "VALIDATES_SYSTEMATICALLY",
                        "target": "methodology_framework",
                        "confidence": analysis["confidence"],
                        "metadata": {
                            "comment_id": comment.id,
                            "strategic_depth": analysis.get("strategic_depth", 0.8)
                        }
                    })
            else:
                relationships.extend(self._fallback_keyword_extraction(comment, issues, solutions))
        
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
        
        for solution_id in solutions.keys():
            for issue_id in issues.keys():
                solution_keywords = set(solutions[solution_id]["keywords"])
                issue_keywords = set(issues[issue_id]["keywords"])
                if solution_keywords.intersection(issue_keywords):
                    relationships.append({
                        "source": solution_id,
                        "relationship": "RESOLVES",
                        "target": issue_id,
                        "confidence": 0.8
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
        
        if "provides" in body_lower or "guidance" in body_lower or "coordinates" in body_lower:
            relationships.append({
                "source": author,
                "relationship": "PROVIDES",
                "target": "strategic_guidance",
                "confidence": 0.6,
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
            "avg_confidence": sum(triplet.confidence for triplet in graph.triplets) / len(graph.triplets) if graph.triplets else 0
        }


graph_service = GraphService()
