import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.graph import PRConversation, PRComment


class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "devin-plugins-service/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    async def fetch_pr_conversation(self, owner: str, repo: str, pr_number: int) -> PRConversation:
        """Fetch PR conversation from GitHub API"""
        async with httpx.AsyncClient() as client:
            pr_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers=self.headers
            )
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            comments_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments",
                headers=self.headers
            )
            comments_response.raise_for_status()
            comments_data = comments_response.json()
            
            review_comments_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments",
                headers=self.headers
            )
            review_comments_response.raise_for_status()
            review_comments_data = review_comments_response.json()
            
            comments = []
            
            for comment in comments_data:
                comments.append(PRComment(
                    id=str(comment["id"]),
                    author=comment["user"]["login"],
                    created_at=datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00")),
                    body=comment["body"],
                    comment_type="comment",
                    metadata={
                        "html_url": comment["html_url"],
                        "updated_at": comment["updated_at"]
                    }
                ))
            
            for comment in review_comments_data:
                comments.append(PRComment(
                    id=str(comment["id"]),
                    author=comment["user"]["login"],
                    created_at=datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00")),
                    body=comment["body"],
                    comment_type="review_comment",
                    metadata={
                        "html_url": comment["html_url"],
                        "diff_hunk": comment.get("diff_hunk", ""),
                        "path": comment.get("path", ""),
                        "position": comment.get("position")
                    }
                ))
            
            comments.sort(key=lambda c: c.created_at)
            
            participants = list(set(comment.author for comment in comments))
            
            return PRConversation(
                pr_number=pr_number,
                repository=f"{owner}/{repo}",
                title=pr_data["title"],
                description=pr_data["body"] or "",
                comments=comments,
                participants=participants,
                created_at=datetime.fromisoformat(pr_data["created_at"].replace("Z", "+00:00")),
                metadata={
                    "html_url": pr_data["html_url"],
                    "state": pr_data["state"],
                    "merged": pr_data.get("merged", False),
                    "base_branch": pr_data["base"]["ref"],
                    "head_branch": pr_data["head"]["ref"]
                }
            )


github_service = GitHubService()
