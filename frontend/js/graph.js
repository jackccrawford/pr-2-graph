// Main graph initialization and data loading

// Get analysis ID from URL parameters or use default
function getAnalysisId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('analysis') || 'aa685847-42a5-43f6-b8a6-59bf7e9154df'; // Default to complex analysis
}

// Load and display graph data
async function loadGraph() {
    const analysisId = getAnalysisId();
    
    try {
        // Show loading state
        document.getElementById('graph').innerHTML = '<div style="color: white; text-align: center; padding: 50px;">Loading graph data...</div>';
        
        // Fetch visualization data from TIN Node Graph API
        const response = await fetch(`/api/tin-graph/visualization/${analysisId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const graphData = await response.json();
        
        // Update page title with analysis info
        if (graphData.metadata) {
            document.querySelector('h1').textContent = `Knowledge Graph Analysis: ${analysisId.substring(0, 8)}`;
            document.querySelector('.header p').textContent = `${graphData.metadata.node_count} nodes, ${graphData.metadata.relationship_count} relationships`;
        }
        
        // Create the interactive graph
        createInteractiveGraph(graphData);
        
        // Update controls with analysis info
        updateControls(graphData);
        
    } catch (error) {
        console.error('Error loading graph:', error);
        document.getElementById('graph').innerHTML = `
            <div style="color: #ff5722; text-align: center; padding: 50px;">
                <h3>Error Loading Graph</h3>
                <p>${error.message}</p>
                <p>Analysis ID: ${analysisId}</p>
                <button onclick="loadGraph()" style="padding: 10px 20px; margin-top: 20px;">Retry</button>
            </div>
        `;
    }
}

// Update controls section with analysis information
function updateControls(graphData) {
    const controlsDiv = document.querySelector('.controls');
    
    // Count node types
    const nodeTypes = {};
    graphData.nodes.forEach(node => {
        nodeTypes[node.type] = (nodeTypes[node.type] || 0) + 1;
    });
    
    // Add node type counts to controls
    let nodeInfo = '<h4>Graph Statistics</h4>';
    Object.entries(nodeTypes).forEach(([type, count]) => {
        const emoji = {
            participant: '👤',
            issue: '🔴',
            solution: '🔵',
            breakthrough: '⚡'
        }[type] || '⚪';
        nodeInfo += `<p>${emoji} ${count} ${type}${count > 1 ? 's' : ''}</p>`;
    });
    
    nodeInfo += `<p>🔗 ${graphData.links.length} relationship${graphData.links.length !== 1 ? 's' : ''}</p>`;
    
    // Add analysis selector
    nodeInfo += '<br><h4>Analysis Selector</h4>';
    nodeInfo += '<button onclick="loadAnalysisList()" style="padding: 5px 10px; margin: 5px;">Browse Analyses</button>';
    nodeInfo += '<button onclick="loadGraph()" style="padding: 5px 10px; margin: 5px;">Refresh</button>';
    
    controlsDiv.innerHTML = nodeInfo;
}

// Load list of available analyses
async function loadAnalysisList() {
    try {
        const response = await fetch('/api/tin-graph/analyses');
        const data = await response.json();
        
        let listHtml = '<h4>Available Analyses</h4>';
        if (data.analyses.length === 0) {
            listHtml += '<p>No analyses found</p>';
        } else {
            data.analyses.forEach(analysis => {
                listHtml += `
                    <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                        <strong>${analysis.title}</strong><br>
                        <small>Nodes: ${analysis.node_count}, Links: ${analysis.relationship_count}</small><br>
                        <button onclick="loadSpecificAnalysis('${analysis.analysis_id}')" style="padding: 3px 8px; margin-top: 5px;">Load</button>
                    </div>
                `;
            });
        }
        
        document.querySelector('.controls').innerHTML = listHtml;
        
    } catch (error) {
        console.error('Error loading analyses:', error);
    }
}

// Load a specific analysis
function loadSpecificAnalysis(analysisId) {
    // Update URL without page reload
    const url = new URL(window.location);
    url.searchParams.set('analysis', analysisId);
    window.history.pushState({}, '', url);
    
    // Load the graph
    loadGraph();
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadGraph();
});

// Handle browser back/forward buttons
window.addEventListener('popstate', function() {
    loadGraph();
});
