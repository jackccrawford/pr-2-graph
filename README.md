# pr-2-graph 📊

Transform GitHub PR conversations into interactive knowledge graphs showing collaboration patterns, problem-solving flows, and breakthrough moments.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)

## 🌟 Overview

**pr-2-graph** is an open-source tool that analyzes GitHub Pull Request conversations and transforms them into interactive knowledge graphs. Perfect for understanding team collaboration patterns, identifying breakthrough moments, and visualizing complex problem-solving flows.

### ✨ Key Features

- **🤝 Multi-Agent Analysis** - Designed for human-AI collaboration patterns
- **🧠 Semantic Relationship Extraction** - Identifies ANALYZES, IMPLEMENTS, FIXES, REVIEWS relationships  
- **📊 Interactive Visualizations** - D3.js physics-based graphs with hover details
- **🔍 Breakthrough Detection** - Spots novel insights that changed conversation direction
- **🎯 Role Analysis** - Distinguishes between strategic analysts, implementers, and coordinators
- **📈 Pattern Recognition** - Learns what collaboration styles produce the best results

## 🏠 Architecture

### 🔧 Core Components

- **📋 Analysis Engine** (`app/core/analyzer.py`) - Main PR conversation analysis
- **🔗 GitHub Integration** (`app/services/github_service.py`) - Fetch PR data from GitHub API
- **🧠 Knowledge Graph Builder** (`app/models/graph.py`) - Construct nodes, edges, and relationships
- **🔌 Relationship Extractor** (`app/services/graph_service.py`) - Semantic relationship detection
- **🎨 Visualization Engine** (`app/exporters/`) - Interactive D3.js graphs and static exports

### 📌 Extensible Design

Built with modularity in mind:

1. **🔌 Pluggable Analysis** - Add new relationship extractors
2. **🎨 Multiple Export Formats** - D3.js, PNG, SVG, JSON, GraphML
3. **⚙️ Configurable Rules** - Customize relationship detection patterns
4. **🔗 API Integration** - Works with any GitHub repository

## 🎯 Use Cases

### 📈 For Development Teams

- **Team Retrospectives** - "How did we solve this complex issue?"
- **Onboarding** - Show new developers how experienced teams collaborate
- **Process Improvement** - Identify patterns that lead to faster problem resolution
- **Knowledge Transfer** - Visualize how expertise flows through the team

### 🔬 For Researchers

- **Human-AI Collaboration Studies** - Analyze how AI agents work with human developers
- **Software Engineering Research** - Study communication patterns in distributed teams
- **Collaboration Pattern Analysis** - Identify what makes teams successful

### Extracted Relationships

The plugin identifies these types of semantic relationships:

- **Participant Actions**: `Cascade ANALYZES authentication_issue`, `Devin IMPLEMENTS message_parsing_fix`
- **Temporal Relationships**: `Comment_5 REPLIES_TO Comment_4`, `Fix_Applied FOLLOWS Problem_Identified`
- **Problem-Solving Chains**: `Authentication_Issue CAUSES Server_Errors`, `Message_Format_Fix RESOLVES API_Errors`
- **Technical Relationships**: `Flutter_App INTEGRATES_WITH TIN_API`, `JWT_Token AUTHENTICATES API_Calls`

## API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `GET /api/plugins` - List all available plugins

### Repo to Graph Plugin Endpoints

- `POST /api/plugins/repo-to-graph/analyze` - Analyze PR conversation
- `GET /api/plugins/repo-to-graph/graph/{analysis_id}` - Get knowledge graph
- `POST /api/plugins/repo-to-graph/test-tin-sidekick` - Test with tin-sidekick data
- `POST /api/plugins/repo-to-graph/test-llm-analysis` - Test LLM-enhanced analysis
- `GET /api/plugins/repo-to-graph/visualize/{analysis_id}` - Interactive D3.js visualization

## Installation & Setup

### Prerequisites

- Python 3.12+
- Poetry for dependency management

### Local Development

```bash
# Install dependencies
poetry install

# Start development server
poetry run fastapi dev app/main.py
```

### Testing

```bash
# Health check
curl -X GET http://127.0.0.1:8000/health

# List plugins
curl -X GET http://127.0.0.1:8000/api/plugins

# Test tin-sidekick analysis (keyword-based)
curl -X POST http://127.0.0.1:8000/api/plugins/repo-to-graph/test-tin-sidekick

# Test LLM-enhanced analysis
curl -X POST http://127.0.0.1:8000/api/plugins/repo-to-graph/test-llm-analysis

# View interactive visualization (replace {analysis_id} with actual ID)
# Open in browser: http://127.0.0.1:8000/api/plugins/repo-to-graph/visualize/{analysis_id}
```

## Test Results

### tin-sidekick PR Analysis

Successfully analyzed the tin-sidekick PR #1 conversation with:

- **30 Comments** from 3 participants
- **90 Knowledge Graph Triplets** extracted
- **Participants Identified**:
  - Devin (AI Flutter Specialist) - 12 comments
  - Jack/Cascade (AI Backend Specialist) - 18 comments
- **Issues Detected**: Authentication Flow, Message Format, API Parsing, Duplication, Debug Execution
- **Solutions Identified**: Message Format Fix, API Parsing Fix, Authentication Fix, Duplication Fix
- **Relationship Types**: ANALYZES, IMPLEMENTS, PROVIDES, REPLIES_TO, RESOLVES

### LLM-Enhanced Analysis

With the new LLM-powered backend:

- **Asymmetric Relationship Types**: DIAGNOSES_ROOT_CAUSE, CONFIRMS_THROUGH_TESTING, VALIDATES_SYSTEMATICALLY, PROVIDES_BREAKTHROUGH
- **Breakthrough Moment Detection**: Identifies novel insights that changed conversation direction
- **Confidence Scoring**: Based on insight novelty and impact rather than keyword presence
- **Participant Role Analysis**: Strategic analyst vs implementation specialist vs coordinator
- **Interactive Visualization**: D3.js physics-based graph with hover details and drag functionality

### Sample Knowledge Graph Output

```json
{
  "nodes": [
    {
      "id": "devin-ai-integration[bot]",
      "label": "Devin (AI Flutter Specialist)",
      "type": "participant",
      "properties": {"role": "ai_flutter_specialist", "comment_count": 12}
    },
    {
      "id": "authentication_issue",
      "label": "Authentication Flow",
      "type": "issue",
      "properties": {"keywords": ["403", "401", "authentication", "auth", "token"]}
    }
  ],
  "edges": [
    {
      "id": "devin-ai-integration[bot]-ANALYZES-authentication_issue",
      "source": "devin-ai-integration[bot]",
      "target": "authentication_issue",
      "relationship": "ANALYZES"
    }
  ],
  "triplets": [
    {
      "subject": "devin-ai-integration[bot]",
      "predicate": "ANALYZES",
      "object": "authentication_issue",
      "confidence": 0.8
    }
  ]
}
```

## Future Plugin Ideas

The extensible architecture supports additional plugins such as:

- **Code Analysis Plugin** - Analyze code changes and patterns
- **Performance Metrics Plugin** - Extract performance-related insights
- **Collaboration Patterns Plugin** - Identify team collaboration patterns
- **Issue Resolution Plugin** - Track issue resolution workflows

## Contributing

To add a new plugin:

1. Create a new file in `app/plugins/`
2. Implement the `BasePlugin` interface
3. Register the plugin in `app/main.py`
4. Add appropriate tests

## License

This project is part of the Devin ecosystem for analyzing AI agent interactions.
