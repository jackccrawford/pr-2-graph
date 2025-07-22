"""Real HuggingFace Transformers PR #39561 conversation data."""

HUGGINGFACE_ERNIE_PR = {
    "pr_number": 39561,
    "repository": "huggingface/transformers",
    "title": "[CI] Fix post merge ernie 4.5",
    "description": """#39339 was merged right before the Ernie 4.5 models and I didn't check with main again :/ fixes the repo consistency based on that

cc @molbap @ArthurZucker""",
    "conversation": """
Comment 1 by vasqu:
#39339 was merged right before the Ernie 4.5 models and I didn't check with main again :/ fixes the repo consistency based on that

cc @molbap @ArthurZucker

Comment 2 by github-actions:
**[For maintainers]** Suggested jobs to run (before merge)

run-slow: ernie4_5, ernie4_5_moe

Comment 3 by HuggingFaceDocBuilderDev:
The docs for this PR live [here](https://moon-ci-docs.huggingface.co/docs/transformers/pr_39561). All of your documentation changes will be reflected on that endpoint. The docs are available until 30 days after the last update.
""",
    "participants": ["vasqu", "github-actions", "HuggingFaceDocBuilderDev", "molbap", "ArthurZucker"],
    "created_at": "2025-07-21T18:06:58Z",
    "metadata": {
        "source": "huggingface/transformers PR #39561",
        "author": "vasqu",
        "is_bot": False,
        "conversation_type": "post_merge_fix",
        "key_features": [
            "Post-merge conflict resolution",
            "CI integration",
            "Automated testing suggestions",
            "Documentation preview",
            "Maintainer coordination"
        ],
        "technical_context": {
            "related_pr": "#39339",
            "models_affected": ["ernie4_5", "ernie4_5_moe"],
            "issue_type": "repo_consistency",
            "automation_involved": ["github-actions", "HuggingFaceDocBuilderDev"]
        },
        "collaboration_pattern": "maintainer_coordination_with_automation"
    }
}
