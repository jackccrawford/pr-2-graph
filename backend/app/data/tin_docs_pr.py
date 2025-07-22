"""Real TIN docs PR #1 conversation data."""

TIN_DOCS_PR_1 = {
    "pr_number": 1,
    "repository": "mvara-ai/tin-docs",
    "title": "Add Devin Plugin System with Repo to Graph Plugin",
    "description": """Enhanced Repo to Graph Plugin with LLM-Powered Asymmetric Relationship Extraction

This PR transforms the "Repo to Graph" plugin from keyword-based relationship extraction to sophisticated LLM-powered semantic analysis using small Ollama language models. The enhancement addresses the "symmetry problem" in generated knowledge graphs by introducing asymmetric relationship types that distinguish strategic vs. tactical contributions in multi-agent PR conversations.

Key Features Added:
- LLM Integration: Ollama service with configurable small models (llama3.2:1b, phi3:mini, qwen2.5:0.5b)
- Asymmetric Relationships: DIAGNOSES_ROOT_CAUSE, CONFIRMS_THROUGH_TESTING, VALIDATES_SYSTEMATICALLY, PROVIDES_BREAKTHROUGH
- Interactive D3.js Visualization: Physics-based node dragging, hover tooltips, confidence-based edge thickness
- Breakthrough Moment Detection: Identifies novel insights that changed conversation direction
- Robust Fallback: Graceful degradation to keyword-based extraction when LLM unavailable
- Async Architecture: Converted GraphService to async for non-blocking LLM calls

Test Results:
- Successfully analyzed tin-sidekick PR with 30 comments from 3 participants
- Generated 90 knowledge graph triplets with semantic relationships
- Interactive visualization renders correctly with all nodes and edges
- Hover tooltips show detailed participant information and confidence scores

Critical Bug Fixed: During development, discovered that 48 out of 49 edges were invalid due to relationships referencing non-existent nodes (e.g., comment IDs instead of participant IDs). Added validation logic to filter relationships and ensure all edges reference valid nodes.

LLM Model Selection: Chose small, fast models optimized for local deployment rather than large cloud models to maintain responsiveness and privacy.

Architecture Decision: Maintained backward compatibility by keeping the existing plugin interface while enhancing the underlying semantic analysis engine.""",
    "conversation": """
Comment 1 by app/devin-ai-integration:
### 🤖 Devin AI Engineer

I'll be helping with this pull request! Here's what you should know:

✅ I will automatically:
- Address comments on this PR. Add '(aside)' to your comment to have me ignore it.
- Look at CI failures and help fix them

⚙️ Control Options:
- [ ] Disable automatic comment and CI monitoring
""",
    "participants": ["app/devin-ai-integration"],
    "created_at": "2025-07-22T04:11:58Z",
    "metadata": {
        "source": "tin-docs PR #1",
        "author": "app/devin-ai-integration",
        "is_bot": True,
        "conversation_type": "plugin_system_development",
        "key_features": [
            "LLM Integration",
            "Asymmetric Relationships", 
            "Interactive D3.js Visualization",
            "Breakthrough Moment Detection",
            "Async Architecture"
        ],
        "technical_achievements": [
            "90 knowledge graph triplets generated",
            "30 comments analyzed from 3 participants",
            "Critical bug fixed: 48/49 invalid edges",
            "Graceful fallback mechanism"
        ]
    }
}
