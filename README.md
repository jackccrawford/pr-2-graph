# pr-2-graph
## GitHub PR Conversation Analysis and Knowledge Graph Generation

[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-2.1.3-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)](https://python-poetry.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.11.7-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![D3.js](https://img.shields.io/badge/D3.js-Interactive_Graphs-F9A03C?style=for-the-badge&logo=d3.js&logoColor=white)](https://d3js.org/)
[![Ollama](https://img.shields.io/badge/Ollama-LLM_Integration-4285F4?style=for-the-badge)](https://ollama.ai/)
[![Status](https://img.shields.io/badge/Status-Active_Development-EAB308?style=for-the-badge)]()
[![Architecture](https://img.shields.io/badge/Architecture-Plugin_Based-9ca3af?style=for-the-badge)]()
[![Analysis](https://img.shields.io/badge/Analysis-Multi--Agent-ff69b4?style=for-the-badge)]()
[![Visualization](https://img.shields.io/badge/Visualization-Interactive-22C55E?style=for-the-badge)]()

> **Note**: This project is currently under active development. APIs are stable with comprehensive documentation.

## Overview

pr-2-graph is an open-source tool that analyzes GitHub Pull Request conversations and transforms them into interactive knowledge graphs. Originally developed as part of Devin AI's plugin system, it has been generalized to help development teams understand collaboration patterns, identify breakthrough moments, and visualize problem-solving flows.

## Architecture: Multi-Model LLM Analysis Pipeline

This system follows a sophisticated multi-stage analysis pattern:

1. **Primary Analysis**: Advanced LLM models extract semantic relationships and collaboration patterns
2. **Critic Review**: Secondary models validate analysis accuracy and completeness
3. **Structured Output**: Specialized formatter models ensure consistent JSON output
4. **Interactive Visualization**: D3.js physics-based knowledge graphs with real-time interaction

## Key Features

### Semantic Analysis
- Extract relationships, roles, and collaboration patterns from PR conversations
- Identify participant contributions and expertise domains
- Map technical decision points and their outcomes
- Support for complex multi-participant discussions

### Breakthrough Detection
- Identify key problem-solving moments and insights
- Track resolution patterns and solution emergence
- Analyze collaboration effectiveness and team dynamics
- Detect innovation and creative problem-solving instances

### Multi-Agent Support
- Specialized analysis for human-AI collaboration patterns
- Recognition of different agent types and their contributions
- Analysis of coordination patterns in mixed teams
- Support for complex multi-agent workflows

### Interactive Visualization
- D3.js-powered knowledge graphs with physics simulation
- Real-time interaction with hover details and drag functionality
- Customizable node and edge styling based on relationship types
- Export capabilities for presentations and documentation

### Extensible Architecture
- Plugin system for custom analysis types
- Configurable LLM models and analysis parameters
- Environment-driven configuration management
- Professional deployment patterns with health monitoring

## Installation

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Jack C Crawford** - *Initial work*