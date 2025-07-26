/**
 * Legacy createInteractiveGraph function for backward compatibility
 * This function now delegates to the new modular component architecture
 * while maintaining the same API for external callers
 */
function createInteractiveGraph(graphData) {
    console.log("Using enhanced knowledge graph visualization");
    
    // Initialize the GraphManager with the data
    // GraphManager handles all the D3.js visualization logic
    // through its modular component architecture
    window.graphManager = new GraphManager({
        containerId: 'graph',
        width: 1200,
        height: 800,
        enableDrilldown: true,
        theme: {
            background: '#0a0a0a',
            textColor: '#ffffff',
            nodeStroke: '#ffffff',
            linkColor: '#64b5f6',
            linkLabelColor: '#90CAF9'
        }
    }).initialize(graphData);
    
    // Return the GraphManager instance for potential direct access
    return window.graphManager;
}
