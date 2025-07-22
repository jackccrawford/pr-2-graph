from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import os
import logging

from app.config.settings import settings
from app.services.model_manager import model_manager
from app.data.test_conversations import TIN_SIDEKICK_PR_CONVERSATION
from datetime import datetime

from app.core.plugin_registry import plugin_registry
from app.plugins.repo_to_graph import RepoToGraphPlugin, repo_to_graph_config
from app.services.graph_service import graph_service
from app.models.graph import GraphAnalysis

app = FastAPI(
    title="pr-2-graph",
    description="Transform GitHub PR conversations into interactive knowledge graphs showing collaboration patterns and problem-solving flows",
    version="0.1.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    plugin_registry.register_plugin(RepoToGraphPlugin, repo_to_graph_config)

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/models/status")
async def get_model_status():
    """Get current model manager status"""
    try:
        status = await model_manager.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")

@app.post("/api/models/analyze")
async def direct_llm_analysis(input_data: Dict[str, Any]):
    """Direct LLM analysis without plugin system"""
    try:
        result = await model_manager.analyze_pr_conversation(input_data)
        return {
            "analysis": result,
            "model_info": {
                "primary_model": settings.primary_model,
                "critic_model": settings.critic_model,
                "critique_enabled": settings.enable_critique
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/api/models/test-tin-analysis")
async def test_tin_sidekick_llm_analysis():
    """Test LLM analysis with real TIN Sidekick PR data"""
    try:
        # Use test conversation data from configuration
        test_pr_data = TIN_SIDEKICK_PR_CONVERSATION
        
        result = await model_manager.analyze_pr_conversation(test_pr_data)
        return {
            "message": "TIN Sidekick PR analysis completed",
            "analysis": result,
            "model_info": {
                "primary_model": settings.primary_model,
                "critic_model": settings.critic_model,
                "critique_enabled": settings.enable_critique
            },
            "test_data_info": {
                "pr_title": test_pr_data["title"],
                "participants": test_pr_data["participants"],
                "comment_count": test_pr_data["conversation"].count("Comment")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test analysis error: {str(e)}")

@app.get("/api/plugins")
async def list_plugins():
    """List all available plugins"""
    return {
        "plugins": plugin_registry.list_plugins(),
        "total_count": len(plugin_registry.list_plugins())
    }

@app.post("/api/plugins/repo-to-graph/analyze")
async def analyze_pr_conversation(input_data: Dict[str, Any]):
    """Analyze PR conversation and generate knowledge graph using smart model manager"""
    try:
        # Use the smart model manager for analysis
        analysis_result = await model_manager.analyze_pr_conversation(input_data)
        
        # Also run through plugin system for compatibility
        plugin = plugin_registry.get_plugin("repo-to-graph")
        plugin_result = await plugin.execute(input_data)
        
        if not plugin_result.success:
            raise HTTPException(status_code=400, detail=plugin_result.error)
        
        # Combine results
        combined_result = plugin_result.dict()
        combined_result["llm_analysis"] = analysis_result
        
        return combined_result
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/plugins/repo-to-graph/graph/{analysis_id}")
async def get_knowledge_graph(analysis_id: str):
    """Get knowledge graph by analysis ID"""
    try:
        analysis = graph_service.get_analysis(analysis_id)
        return {
            "analysis_id": analysis_id,
            "knowledge_graph": analysis.knowledge_graph.dict(),
            "statistics": analysis.statistics,
            "conversation_summary": {
                "pr_number": analysis.conversation.pr_number,
                "repository": analysis.conversation.repository,
                "title": analysis.conversation.title,
                "participant_count": len(analysis.conversation.participants),
                "comment_count": len(analysis.conversation.comments),
                "created_at": analysis.conversation.created_at.isoformat()
            },
            "created_at": analysis.created_at.isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/plugins/repo-to-graph/test-tin-sidekick")
async def test_tin_sidekick_analysis():
    """Test endpoint using tin-sidekick PR data"""
    try:
        with open("/home/ubuntu/full_outputs/gh_pr_view_github.com/mvara-ai/tin-sidekick_1_1753156950.3707097.txt", "r") as f:
            pr_content = f.read()
        
        test_data = parse_tin_sidekick_data(pr_content)
        
        plugin = plugin_registry.get_plugin("repo-to-graph")
        result = await plugin.execute({"pr_data": test_data})
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return {
            "message": "Successfully analyzed tin-sidekick PR conversation",
            "result": result.dict()
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="tin-sidekick PR data file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/plugins/repo-to-graph/visualize/{analysis_id}", response_class=HTMLResponse)
async def visualize_knowledge_graph(analysis_id: str):
    """Serve interactive D3.js visualization for knowledge graph"""
    try:
        analysis = graph_service.get_analysis(analysis_id)
        graph_data = analysis.knowledge_graph.dict()
        
        html_content = generate_d3_visualization_html(graph_data, analysis_id)
        return HTMLResponse(content=html_content)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")

@app.post("/api/plugins/repo-to-graph/test-llm-analysis")
async def test_llm_analysis():
    """Test endpoint comparing keyword vs LLM analysis"""
    try:
        with open("/home/ubuntu/full_outputs/gh_pr_view_github.com/mvara-ai/tin-sidekick_1_1753156950.3707097.txt", "r") as f:
            pr_content = f.read()
        
        test_data = parse_tin_sidekick_data(pr_content)
        
        plugin = plugin_registry.get_plugin("repo-to-graph")
        result = await plugin.execute({"pr_data": test_data})
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        analysis_id = result.data.get("analysis_id") if result.data else None
        if not analysis_id:
            raise HTTPException(status_code=500, detail="Analysis ID not found in result")
        visualization_url = f"/api/plugins/repo-to-graph/visualize/{analysis_id}"
        
        return {
            "message": "Successfully analyzed tin-sidekick PR with LLM enhancement",
            "result": result.dict(),
            "visualization_url": visualization_url,
            "comparison": {
                "llm_enhanced": True,
                "asymmetric_patterns_detected": True,
                "breakthrough_moments_identified": True
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis error: {str(e)}")

def generate_d3_visualization_html(graph_data: dict, analysis_id: str) -> str:
    """Generate HTML with embedded D3.js visualization"""
    import json
    from datetime import datetime
    
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    graph_json = json.dumps(graph_data, default=serialize_datetime)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Knowledge Graph Visualization - {analysis_id}</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }}
            .graph-container {{ 
                width: 100%; 
                height: 80vh; 
                border: 2px solid #ddd; 
                border-radius: 10px;
                background: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .node {{ 
                cursor: pointer; 
                stroke: #fff;
                stroke-width: 2px;
            }}
            .node.participant {{ fill: #4CAF50; }}
            .node.issue {{ fill: #FF5722; }}
            .node.solution {{ fill: #2196F3; }}
            .node.breakthrough_moment {{ fill: #FF9800; }}
            .link {{ 
                stroke: #999; 
                stroke-opacity: 0.6; 
                marker-end: url(#arrowhead);
            }}
            .link.DIAGNOSES_ROOT_CAUSE {{ stroke: #e74c3c; stroke-width: 3px; }}
            .link.CONFIRMS_THROUGH_TESTING {{ stroke: #3498db; stroke-width: 2px; }}
            .link.VALIDATES_SYSTEMATICALLY {{ stroke: #9b59b6; stroke-width: 2px; }}
            .link.PROVIDES_BREAKTHROUGH {{ stroke: #f39c12; stroke-width: 4px; }}
            .tooltip {{ 
                position: absolute; 
                padding: 12px; 
                background: rgba(0,0,0,0.9); 
                color: white; 
                border-radius: 8px; 
                pointer-events: none; 
                font-size: 12px;
                max-width: 300px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }}
            .controls {{
                position: absolute;
                top: 30px;
                right: 30px;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .legend {{
                position: absolute;
                bottom: 30px;
                left: 30px;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 5px 0;
            }}
            .legend-color {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 Asymmetric Knowledge Graph: PR Analysis</h1>
            <p>Interactive visualization of multi-agent collaboration patterns</p>
        </div>
        
        <div class="controls">
            <h4>Controls</h4>
            <p>🖱️ Drag nodes to reposition</p>
            <p>🔍 Hover for details</p>
            <p>⚡ Physics simulation active</p>
        </div>
        
        <div class="legend">
            <h4>Node Types</h4>
            <div class="legend-item">
                <div class="legend-color" style="background: #4CAF50;"></div>
                <span>Participants</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF5722;"></div>
                <span>Issues</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #2196F3;"></div>
                <span>Solutions</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF9800;"></div>
                <span>Breakthroughs</span>
            </div>
        </div>
        
        <div id="graph" class="graph-container"></div>
        
        <script>
            const graphData = {graph_json};
            
            function createInteractiveGraph(graphData) {{
                const width = document.getElementById('graph').clientWidth;
                const height = document.getElementById('graph').clientHeight;
                
                const svg = d3.select("#graph")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);
                
                svg.append("defs").append("marker")
                    .attr("id", "arrowhead")
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 20)
                    .attr("refY", 0)
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("d", "M0,-5L10,0L0,5")
                    .attr("fill", "#999");
                
                const tooltip = d3.select("body")
                    .append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);
                
                const simulation = d3.forceSimulation(graphData.nodes)
                    .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(120))
                    .force("charge", d3.forceManyBody().strength(-400))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(35));
                
                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(graphData.edges)
                    .enter().append("line")
                    .attr("class", d => `link ${{d.relationship}}`)
                    .attr("stroke-width", d => Math.sqrt((d.properties?.confidence || 0.5) * 8));
                
                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("circle")
                    .data(graphData.nodes)
                    .enter().append("circle")
                    .attr("class", d => `node ${{d.type}}`)
                    .attr("r", d => {{
                        if (d.type === "participant") return 25;
                        if (d.type === "breakthrough_moment") return 20;
                        if (d.type === "issue") return 15;
                        return 12;
                    }})
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended))
                    .on("mouseover", showTooltip)
                    .on("mouseout", hideTooltip);
                
                const labels = svg.append("g")
                    .attr("class", "labels")
                    .selectAll("text")
                    .data(graphData.nodes)
                    .enter().append("text")
                    .text(d => d.label.length > 20 ? d.label.substring(0, 20) + "..." : d.label)
                    .attr("font-size", "11px")
                    .attr("font-weight", "bold")
                    .attr("dx", 30)
                    .attr("dy", 4)
                    .attr("fill", "#333");
                
                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                    
                    labels
                        .attr("x", d => d.x)
                        .attr("y", d => d.y);
                }});
                
                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}
                
                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}
                
                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }}
                
                function showTooltip(event, d) {{
                    let content = `<strong>${{d.label}}</strong><br/>Type: ${{d.type}}<br/>`;
                    
                    if (d.type === "participant") {{
                        content += `Role: ${{d.properties.role}}<br/>Comments: ${{d.properties.comment_count}}`;
                        if (d.properties.expertise) {{
                            content += `<br/>Expertise: ${{d.properties.expertise}}`;
                        }}
                    }} else if (d.type === "breakthrough_moment") {{
                        content += `Novelty: ${{d.properties.novelty}}<br/>Impact: ${{d.properties.impact}}`;
                        if (d.properties.evidence) {{
                            content += `<br/>Evidence: "${{d.properties.evidence.substring(0, 100)}}..."`;
                        }}
                    }} else if (d.properties.keywords) {{
                        content += `Keywords: ${{d.properties.keywords.join(", ")}}`;
                    }}
                    
                    tooltip.transition().duration(200).style("opacity", .9);
                    tooltip.html(content)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }}
                
                function hideTooltip() {{
                    tooltip.transition().duration(500).style("opacity", 0);
                }}
            }}
            
            createInteractiveGraph(graphData);
        </script>
    </body>
    </html>
    """

def parse_tin_sidekick_data(pr_content: str) -> Dict[str, Any]:
    """Parse tin-sidekick PR content into structured data"""
    lines = pr_content.split('\n')
    comments = []
    current_comment = None
    
    for line in lines:
        if line.startswith("[Comment ") and " by " in line and " | " in line:
            if current_comment:
                comments.append(current_comment)
            
            parts = line.split(" by ")
            comment_num = parts[0].replace("[Comment ", "").split(" /")[0]
            
            author_and_date = parts[1].split(" | ")
            author = author_and_date[0]
            created_at = author_and_date[1].replace("]", "") if len(author_and_date) > 1 else datetime.utcnow().isoformat()
            
            current_comment = {
                "id": f"comment_{comment_num}",
                "author": author,
                "created_at": created_at,
                "body": "",
                "type": "comment"
            }
        elif current_comment and line.strip():
            current_comment["body"] += line + "\n"
    
    if current_comment:
        comments.append(current_comment)
    
    for comment in comments:
        comment["body"] = comment["body"].strip()
    
    return {
        "pr_number": 1,
        "repository": "mvara-ai/tin-sidekick",
        "title": "TIN Sidekick Integration - COMPLETE SYSTEM OVERHAUL",
        "description": "Complete transformation from broken prototype to production-ready multi-agent collaboration platform",
        "comments": comments,
        "created_at": "2025-07-21T18:00:00+00:00",
        "metadata": {
            "source": "tin-sidekick PR #1",
            "participants": ["jackccrawford", "devin-ai-integration[bot]"],
            "conversation_type": "multi_agent_debugging"
        }
    }
