function initializeGraph() {
    const sampleGraphData = {
        nodes: [
            { id: "1", label: "Sample Participant", type: "participant", properties: { role: "developer", comment_count: 5 } },
            { id: "2", label: "Sample Issue", type: "issue", properties: { keywords: ["bug", "critical"] } },
            { id: "3", label: "Sample Solution", type: "solution", properties: { keywords: ["fix", "implementation"] } }
        ],
        edges: [
            { source: "1", target: "2", relationship: "DIAGNOSES_ROOT_CAUSE", properties: { confidence: 0.8 } },
            { source: "1", target: "3", relationship: "PROVIDES_BREAKTHROUGH", properties: { confidence: 0.9 } }
        ]
    };
    
    createInteractiveGraph(sampleGraphData);
}

async function loadGraphData(analysisId) {
    try {
        const response = await fetch(`/api/knowledge-graph/${analysisId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const graphData = await response.json();
        createInteractiveGraph(graphData);
    } catch (error) {
        console.error('Error loading graph data:', error);
        initializeGraph();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('analysis');
    
    if (analysisId) {
        loadGraphData(analysisId);
    } else {
        initializeGraph();
    }
});
