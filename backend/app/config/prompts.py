"""Prompt templates for pr-2-graph analysis."""

# System prompts for different analysis roles
ANALYSIS_SYSTEM_PROMPTS = {
    "primary_analyzer": """You are an expert at analyzing GitHub PR conversations and extracting collaboration patterns.

Analyze the conversation and identify:
1. Key relationships between participants (ANALYZES, IMPLEMENTS, FIXES, SUGGESTS, etc.)
2. Breakthrough moments where problems are solved
3. Participant roles and contributions
4. Technical decision points

Return a structured JSON response.""",

    "critic_reviewer": """You are a quality assurance critic for PR conversation analysis.

Review the analysis for:
1. Accuracy - Are relationships supported by the text?
2. Completeness - Are important patterns missing?
3. Confidence - Are confidence scores realistic?
4. Consistency - Do all relationships make sense together?

Provide specific, actionable feedback.""",

    "json_formatter": """You extract and format PR conversation analysis into structured JSON.

If analysis is incomplete, respond:
'Analysis incomplete. Please regenerate.'

If complete, return JSON in the following format:
{
  "analysis": {
    "key_relationships": [
      {
        "participant": "participant_name",
        "role": "ANALYZES" | "IMPLEMENTS" | "FIXES" | "SUGGESTS",
        "frequency": "high" | "moderate" | "low",
        "notes": "description"
      }
    ],
    "breakthrough_moments": [
      {
        "timestamp": "ISO_timestamp",
        "comment": "key_insight_text",
        "resolution": "problem_solved"
      }
    ],
    "participant_roles_and_contributions": [
      {
        "participant": "name",
        "role": "primary_role",
        "contributions": ["list", "of", "contributions"]
      }
    ],
    "technical_decision_points": [
      {
        "timestamp": "ISO_timestamp",
        "decision": "decision_made",
        "outcome": "result"
      }
    ],
    "confidence": 0.0-1.0
  }
}

Never explain or add comments. Only return structured JSON or an error message."""
}

# Analysis prompt templates
PARTICIPANT_ANALYSIS_PROMPT = """
Analyze this PR comment and identify the participant's role and contribution type.

Author: {author}
Created: {created_at}
Comment: {body}

Identify:
1. Role (strategic_analyst, implementation_specialist, coordinator, domain_expert)
2. Contribution type (root_cause_analysis, empirical_testing, process_innovation, architectural_insight, systematic_validation)
3. Expertise domain (backend_architecture, frontend_development, system_integration, project_management)
4. Insight novelty (0.0-1.0 based on breakthrough potential and uniqueness)
5. Evidence quotes (specific phrases that support the analysis)

Respond with JSON:
{{
  "role": "strategic_analyst",
  "contribution_type": "root_cause_analysis", 
  "expertise": "backend_architecture",
  "insight_novelty": 0.85,
  "evidence": ["specific quote from comment"],
  "confidence": 0.90
}}
"""

RELATIONSHIP_EXTRACTION_PROMPT = """
Analyze the relationship between these two entities in the given context.

Entity 1: {entity1_type} - {entity1_label}
Entity 2: {entity2_type} - {entity2_label}
Context: {context}

Determine the semantic relationship, focusing on asymmetric patterns:

Strategic relationships:
- DIAGNOSES_ROOT_CAUSE (deep technical analysis)
- PROVIDES_BREAKTHROUGH (novel insight that changes direction)
- VALIDATES_HYPOTHESIS (confirms strategic analysis)
- ESTABLISHES_METHODOLOGY (creates new process/framework)

Tactical relationships:
- CONFIRMS_THROUGH_TESTING (empirical validation)
- IMPLEMENTS_SOLUTION (technical execution)
- APPLIES_SYSTEMATICALLY (follows established process)
- VALIDATES_INTEGRATION (end-to-end verification)

Coordination relationships:
- ORCHESTRATES_COLLABORATION (manages multi-agent workflow)
- COORDINATES_WORKFLOW (process management)
- PROVIDES_STRATEGIC_OVERSIGHT (high-level guidance)

Respond with JSON:
{{
  "type": "DIAGNOSES_ROOT_CAUSE",
  "confidence": 0.92,
  "evidence": "specific quote supporting relationship",
  "asymmetric": true,
  "strategic_depth": 0.85,
  "novelty_impact": 0.90
}}
"""

BREAKTHROUGH_ANALYSIS_PROMPT = """
Analyze this conversation and identify breakthrough moments, novel insights, and problem-solving patterns.

Conversation:
{conversation}

Identify:
1. Breakthrough moments (insights that changed conversation direction)
2. Novel contributions (unique approaches or discoveries)
3. Problem-solving chains (how understanding evolved)
4. Knowledge transfer patterns (who learned from whom)

Focus on asymmetric contributions where one participant provided significantly more strategic value than others.

Respond with JSON:
{{
  "breakthrough_moments": [
    {{
      "moment_id": "cascade_format_discovery",
      "participant": "jackccrawford",
      "insight_type": "root_cause_analysis",
      "description": "Identified exact JSON payload format issue",
      "evidence": "After extensive API testing, I've identified...",
      "novelty": 0.95,
      "impact": 0.90,
      "timestamp": "comment_12"
    }}
  ],
  "knowledge_transfer_chains": [
    {{
      "chain_id": "diagnostic_validation",
      "sequence": [
        {{"participant": "cascade", "action": "HYPOTHESIZES", "target": "message_format_issue"}},
        {{"participant": "jack", "action": "VALIDATES_SYSTEMATICALLY", "target": "cascade_hypothesis"}},
        {{"participant": "devin", "action": "CONFIRMS_EMPIRICALLY", "target": "format_fix"}}
      ]
    }}
  ],
  "asymmetric_patterns": [
    {{
      "pattern_type": "strategic_vs_tactical",
      "strategic_contributor": "cascade",
      "tactical_contributor": "devin",
      "coordination_contributor": "jack",
      "evidence": "Cascade provided root cause analysis while Devin focused on implementation testing"
    }}
  ]
}}
"""

CONFIDENCE_SCORING_PROMPT = """
Score the confidence and impact of this relationship based on evidence quality and insight novelty.

Relationship: {relationship_type}
Evidence: {evidence}
Context: {context}

Scoring criteria:
- Evidence quality (0.0-1.0): How well does evidence support the relationship?
- Insight novelty (0.0-1.0): How unique/breakthrough is this insight?
- Strategic impact (0.0-1.0): How much did this change the conversation direction?
- Technical precision (0.0-1.0): How technically accurate is the analysis?

Respond with JSON:
{{
  "confidence": 0.88,
  "evidence_quality": 0.90,
  "insight_novelty": 0.85,
  "strategic_impact": 0.92,
  "technical_precision": 0.80,
  "overall_score": 0.87
}}
"""
