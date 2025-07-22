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

pr-2-graph uses a sophisticated three-stage LLM pipeline with custom Ollama models, each specialized for specific aspects of PR conversation analysis:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   pr-analyzer   │───▶│   pr-critic      │───▶│  pr-formatter   │
│   (Primary)     │    │   (Quality)      │    │  (Structure)    │
│ gemma3n:e2b base│    │ qwen3:1.7b base  │    │ phi4-mini base  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        ▲                        ▲                        ▲
        │                        │                        │
   Modelfile with           Modelfile with          Modelfile with
   PR analysis              critique focus          JSON formatting
   instructions             instructions            instructions
```

### Model Specialization

1. **pr-analyzer** (Primary Analysis)
   - **Base Model**: gemma3n:e2b (5.6GB)
   - **Purpose**: Extract semantic relationships, identify collaboration patterns, detect breakthrough moments
   - **Specialization**: GitHub PR conversation analysis with focus on multi-agent workflows

2. **pr-critic** (Quality Review)
   - **Base Model**: qwen3:1.7b (1.4GB)
   - **Purpose**: Validate analysis accuracy, identify missing elements, suggest improvements
   - **Specialization**: Quality assurance for PR analysis with focus on completeness and consistency

3. **pr-formatter** (Structured Output)
   - **Base Model**: phi4-mini:3.8b (2.5GB)
   - **Purpose**: Extract and format analysis into structured JSON, ensure data consistency
   - **Specialization**: JSON formatting and data structure validation

### Pipeline Benefits
- **Memory Efficient**: Models loaded/unloaded dynamically based on system resources
- **Quality Assured**: Multi-stage validation ensures accurate and complete analysis
- **Specialized Performance**: Each model optimized for its specific task
- **Fallback Support**: Graceful degradation when models are unavailable

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
- [Ollama](https://ollama.ai/) for local LLM inference
- Git for version control

### Local Development

```bash
# Clone repository
git clone https://github.com/your-username/pr-2-graph.git
cd pr-2-graph

# Install dependencies
poetry install

# Set up custom Ollama models
cd ollama-models
./setup_pr_models.sh

# Configure environment
cp .env .env.local
# Edit .env.local with your settings

# Start server with custom models
./run_server.sh
```

### Custom Model Setup

The system uses three specialized Ollama models. Run the setup script to create them:

```bash
cd ollama-models
./setup_pr_models.sh
```

This creates:
- `pr-analyzer:latest` - Primary PR conversation analysis
- `pr-critic:latest` - Quality review and validation
- `pr-formatter:latest` - JSON formatting and structure

Update your `.env.local` to use these models:
```bash
PRIMARY_MODEL=pr-analyzer:latest
CRITIC_MODEL=pr-critic:latest
FORMATTER_MODEL=pr-formatter:latest
```

### Testing

```bash
# Health check
curl -X GET http://localhost:7700/health

# Model manager status
curl -X GET http://localhost:7700/api/models/status

# Test with TIN Sidekick PR data
curl -X POST http://localhost:7700/api/models/test-tin-analysis

# Test with TIN Docs PR data
curl -X POST http://localhost:7700/api/models/test-tin-docs-analysis

# Test with HuggingFace PR data
curl -X POST http://localhost:7700/api/models/test-huggingface-analysis

# Direct LLM analysis
curl -X POST http://localhost:7700/api/models/analyze \
  -H "Content-Type: application/json" \
  -d '{"conversation": "Your PR conversation text here"}'

# Interactive API documentation
# Open in browser: http://localhost:7700/docs
```

## Test Results

### Multi-Model Pipeline Performance

Our custom Ollama models demonstrate significant improvements over generic prompts:

| **Test Case** | **Confidence** | **Participants** | **Relationships** | **Breakthrough Moments** |
|---------------|----------------|------------------|-------------------|-------------------------|
| TIN Sidekick PR | 0.7 | 2 | 2 | 1 ("CODE IS TRUTH") |
| TIN Docs PR | 0.7 | 1 | 3 | 0 |
| HuggingFace PR | **0.85** | **5** | **5** | **2** |

### Real-World Analysis Examples

#### HuggingFace Transformers PR #39561
**Collaboration Pattern**: maintainer_coordination_with_automation
- **Human Contributors**: vasqu (issue identifier), molbap & ArthurZucker (maintainers)
- **Automation**: github-actions (testing), HuggingFaceDocBuilderDev (docs)
- **Key Insight**: Post-merge conflict resolution with Ernie 4.5 model updates
- **Breakthrough Moments**: Issue identification and automated documentation preview

#### TIN Sidekick PR Analysis
**Collaboration Pattern**: human_ai_debugging_workflow

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