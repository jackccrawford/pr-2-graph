import json
from typing import Dict, Any, List
from datetime import datetime
from app.plugins.base import BasePlugin, PluginConfig, PluginResult
from app.models.graph import PRConversation, PRComment
from app.services.graph_service import graph_service


class RepoToGraphPlugin(BasePlugin):
    """Plugin that converts repository PR conversations to knowledge graphs"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any]) -> PluginResult:
        """Execute the repo-to-graph conversion"""
        try:
            if "pr_data" in input_data:
                conversation = self._parse_pr_data(input_data["pr_data"])
            elif "github_url" in input_data:
                conversation = await self._fetch_from_github(input_data["github_url"])
            else:
                return PluginResult(
                    success=False,
                    error="Missing required input: 'pr_data' or 'github_url'"
                )
            
            analysis_id = await graph_service.create_analysis(conversation)
            analysis = graph_service.get_analysis(analysis_id)
            
            return PluginResult(
                success=True,
                data={
                    "analysis_id": analysis_id,
                    "knowledge_graph": analysis.knowledge_graph.dict(),
                    "statistics": analysis.statistics,
                    "conversation_summary": {
                        "pr_number": conversation.pr_number,
                        "repository": conversation.repository,
                        "participant_count": len(conversation.participants),
                        "comment_count": len(conversation.comments)
                    }
                },
                metadata={
                    "processing_time": "calculated_in_service",
                    "extraction_method": "semantic_analysis"
                }
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Plugin execution failed: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the input/output schema for this plugin"""
        return {
            "input": {
                "type": "object",
                "properties": {
                    "pr_data": {
                        "type": "object",
                        "description": "Raw PR conversation data"
                    },
                    "github_url": {
                        "type": "string",
                        "description": "GitHub PR URL to fetch data from"
                    }
                },
                "oneOf": [
                    {"required": ["pr_data"]},
                    {"required": ["github_url"]}
                ]
            },
            "output": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "analysis_id": {"type": "string"},
                            "knowledge_graph": {"type": "object"},
                            "statistics": {"type": "object"},
                            "conversation_summary": {"type": "object"}
                        }
                    },
                    "error": {"type": "string"}
                }
            }
        }
    
    def _parse_pr_data(self, pr_data: Dict[str, Any]) -> PRConversation:
        """Parse PR data into PRConversation model"""
        comments = []
        
        if "comments" in pr_data:
            for comment_data in pr_data["comments"]:
                comments.append(PRComment(
                    id=comment_data.get("id", str(len(comments))),
                    author=comment_data.get("author", "unknown"),
                    created_at=datetime.fromisoformat(comment_data.get("created_at", datetime.utcnow().isoformat())),
                    body=comment_data.get("body", ""),
                    comment_type=comment_data.get("type", "comment"),
                    metadata=comment_data.get("metadata", {})
                ))
        
        participants = list(set(comment.author for comment in comments))
        
        return PRConversation(
            pr_number=pr_data.get("pr_number", 1),
            repository=pr_data.get("repository", "unknown/repo"),
            title=pr_data.get("title", "PR Conversation"),
            description=pr_data.get("description", ""),
            comments=comments,
            participants=participants,
            created_at=datetime.fromisoformat(pr_data.get("created_at", datetime.utcnow().isoformat())),
            metadata=pr_data.get("metadata", {})
        )
    
    async def _fetch_from_github(self, github_url: str) -> PRConversation:
        """Fetch PR data from GitHub API"""
        raise NotImplementedError("GitHub API integration not yet implemented")


repo_to_graph_config = PluginConfig(
    name="repo-to-graph",
    version="1.0.0",
    description="Converts repository PR conversations to knowledge graphs showing multi-agent collaboration patterns",
    enabled=True
)
