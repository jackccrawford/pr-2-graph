/**
 * GraphManager.js
 * Main integration component for the knowledge graph visualization
 * Orchestrates all visualization components and manages graph state
 */
class GraphManager {
    /**
     * Constructor for the GraphManager
     * @param {Object} config - Configuration options
     */
    constructor(config = {}) {
        // Configuration with defaults
        this.config = {
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
            },
            ...config
        };
        
        // Initialize state
        this.graphData = null;
        this.selectedNode = null;
        this.selectedLink = null;
        
        // Component references
        this.graphViz = null;
        this.drilldownPanel = null;
    }
    
    /**
     * Initialize the graph visualization
     * @param {Object} graphData - Data for the graph visualization
     */
    initialize(graphData) {
        console.log("Initializing enhanced graph visualization...");
        
        // Store reference to graph data
        this.graphData = graphData;
        
        // Create main visualization component
        this.graphViz = new GraphVisualization({
            containerId: this.config.containerId,
            width: this.config.width,
            height: this.config.height,
            theme: this.config.theme
        });
        
        // Initialize graph visualization
        this.graphViz.initialize(graphData);
        
        // Set up drilldown panel if enabled
        if (this.config.enableDrilldown) {
            this.drilldownPanel = new DrilldownPanel({
                theme: this.config.theme
            });
            
            // Add click handler to nodes for drilldown
            this.setupNodeClickHandlers();
        }
        
        // Initialize graph controls
        this.graphControls = new GraphControls({
            containerId: this.config.containerId,
            graphManager: this
        });
        
        console.log("Graph visualization initialized successfully");
        
        return this;
    }
    
    /**
     * Update the graph with new data
     * @param {Object} graphData - New data for the graph
     */
    updateData(graphData) {
        // Store reference to new data
        this.graphData = graphData;
        
        // Update visualization
        if (this.graphViz) {
            this.graphViz.updateData(graphData);
        }
        
        // Reset selection
        this.selectedNode = null;
        this.selectedLink = null;
        
        return this;
    }
    
    /**
     * Set up click handlers for nodes to show drilldown panel
     */
    setupNodeClickHandlers() {
        // Get all node elements
        const nodeElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".nodes circle");
        
        // Add click event listeners
        nodeElements.on("click", (event, d) => {
            event.stopPropagation(); // Prevent propagation
            this.handleNodeClick(d);
        });
        
        // Get all link elements
        const linkElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".links line");
        
        // Add click event listeners to links
        linkElements.on("click", (event, d) => {
            event.stopPropagation(); // Prevent propagation
            this.handleLinkClick(d);
        });
        
        // Add click event listener to SVG background to close panel
        d3.select(`#${this.config.containerId} svg`).on("click", () => {
            if (this.drilldownPanel) {
                this.drilldownPanel.hide();
            }
        });
    }
    
    /**
     * Handle node click event
     * @param {Object} node - The clicked node
     */
    handleNodeClick(node) {
        // Store selected node
        this.selectedNode = node;
        
        // Show drilldown panel for node
        if (this.drilldownPanel) {
            this.drilldownPanel.showNode(
                node, 
                this.graphData.nodes, 
                this.graphData.links
            );
        }
        
        // Highlight node and related nodes/links
        this.highlightRelatedElements(node);
    }
    
    /**
     * Handle link click event
     * @param {Object} link - The clicked link
     */
    handleLinkClick(link) {
        // Store selected link
        this.selectedLink = link;
        
        // Show drilldown panel for link
        if (this.drilldownPanel) {
            this.drilldownPanel.showLink(link);
        }
    }
    
    /**
     * Highlight node and its related elements
     * @param {Object} node - The node to highlight
     */
    highlightRelatedElements(node) {
        // Get all node and link elements
        const nodeElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".nodes circle");
        
        const linkElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".links line");
        
        // Reset all elements first
        nodeElements.attr("opacity", 0.4)
            .attr("stroke-width", 2);
        
        linkElements.attr("opacity", 0.2)
            .attr("stroke-width", d => this.getStrokeWidth(d));
        
        // Find related nodes and links
        const relatedLinks = this.graphData.links.filter(link => 
            link.source.id === node.id || link.target.id === node.id
        );
        
        const relatedNodeIds = new Set();
        relatedNodeIds.add(node.id); // Add the selected node
        
        relatedLinks.forEach(link => {
            if (link.source.id === node.id) {
                relatedNodeIds.add(link.target.id);
            } else {
                relatedNodeIds.add(link.source.id);
            }
        });
        
        // Highlight the selected node and related nodes
        nodeElements.filter(d => relatedNodeIds.has(d.id))
            .attr("opacity", 1)
            .attr("stroke-width", 3);
        
        // Highlight related links
        linkElements.filter(d => 
            d.source.id === node.id || d.target.id === node.id
        ).attr("opacity", 1)
         .attr("stroke-width", d => this.getStrokeWidth(d) * 1.5);
    }
    
    /**
     * Reset highlight state of all elements
     */
    resetHighlighting() {
        // Get all node and link elements
        const nodeElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".nodes circle");
        
        const linkElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".links line");
        
        // Reset all elements
        nodeElements.attr("opacity", 1)
            .attr("stroke-width", 2);
        
        linkElements.attr("opacity", 0.8)
            .attr("stroke-width", d => this.getStrokeWidth(d));
    }
    
    /**
     * Get stroke width for a link
     * @param {Object} link - The link
     * @returns {number} The stroke width
     */
    getStrokeWidth(link) {
        // Base width
        let width = 2;
        
        // Adjust based on confidence if available
        if (link.properties && link.properties.confidence) {
            width = 1 + (link.properties.confidence * 3);
        }
        
        return width;
    }
    
    /**
     * Destroy the graph visualization and clean up
     */
    destroy() {
        // Clear the container
        d3.select(`#${this.config.containerId}`).selectAll("*").remove();
        
        // Remove drilldown panel if exists
        if (this.drilldownPanel) {
            const panel = document.getElementById(this.drilldownPanel.config.containerId);
            if (panel) {
                panel.remove();
            }
        }
        
        // Reset references
        this.graphViz = null;
        this.drilldownPanel = null;
        this.graphData = null;
    }
}

/**
 * Legacy compatibility function - wraps the new component architecture
 * for backward compatibility with existing code
 * @param {Object} graphData - Graph data
 */
function createInteractiveGraph(graphData) {
    // Initialize graph manager with the data
    window.graphManager = new GraphManager({
        containerId: 'graph',
        width: 1200,
        height: 800,
        enableDrilldown: true
    }).initialize(graphData);
}
