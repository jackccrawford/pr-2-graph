/**
 * GraphVisualization.js
 * Core visualization component that manages the D3.js force-directed graph
 */
class GraphVisualization {
    /**
     * Constructor for the graph visualization component
     * @param {Object} config - Configuration options
     * @param {string} config.containerId - ID of the container element
     * @param {number} config.width - Width of the visualization
     * @param {number} config.height - Height of the visualization
     * @param {Object} config.theme - Theme configuration for the visualization
     */
    constructor(config = {}) {
        // Default configuration
        this.config = {
            containerId: 'graph',
            width: 1200,
            height: 800,
            theme: {
                background: '#0a0a0a',
                textColor: '#ffffff',
                nodeStroke: '#ffffff',
                linkColor: '#64b5f6',
                linkLabelColor: '#90CAF9'
            },
            ...config
        };
        
        // Component references
        this.nodeRenderer = null;
        this.edgeRenderer = null;
        this.tooltipManager = null;
        
        // D3 elements
        this.svg = null;
        this.simulation = null;
        
        // Data references
        this.graphData = null;
        this.nodes = [];
        this.links = [];
    }
    
    /**
     * Initialize the graph visualization
     * @param {Object} graphData - Data for the graph visualization
     */
    initialize(graphData) {
        // Clear any existing graph
        d3.select(`#${this.config.containerId}`).selectAll("*").remove();
        
        // Store reference to graph data
        this.graphData = graphData;
        this.nodes = graphData.nodes || [];
        this.links = graphData.links || [];
        
        // Create the SVG container
        this.svg = d3.select(`#${this.config.containerId}`)
            .append("svg")
            .attr("width", this.config.width)
            .attr("height", this.config.height)
            .style("background", this.config.theme.background)
            .style("border-radius", "8px");
            
        // Initialize components
        this.initializeComponents();
        
        // Setup force simulation
        this.setupSimulation();
        
        // Return reference to self for chaining
        return this;
    }
    
    /**
     * Initialize all sub-components
     */
    initializeComponents() {
        // Import required components
        this.tooltipManager = new TooltipManager({
            theme: this.config.theme
        });
        
        this.edgeRenderer = new EdgeRenderer({
            svg: this.svg,
            links: this.links,
            theme: this.config.theme
        });
        
        this.nodeRenderer = new NodeRenderer({
            svg: this.svg,
            nodes: this.nodes,
            theme: this.config.theme,
            tooltipManager: this.tooltipManager,
            onDragStart: this.handleDragStart.bind(this),
            onDrag: this.handleDrag.bind(this),
            onDragEnd: this.handleDragEnd.bind(this)
        });
    }
    
    /**
     * Setup the force simulation for the graph
     */
    setupSimulation() {
        this.simulation = d3.forceSimulation(this.nodes)
            .force("link", d3.forceLink(this.links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(this.config.width / 2, this.config.height / 2))
            .force("collision", d3.forceCollide().radius(35))
            .on("tick", this.handleSimulationTick.bind(this));
    }
    
    /**
     * Handle simulation tick events
     */
    handleSimulationTick() {
        // Update edge positions
        this.edgeRenderer.updatePositions();
        
        // Update node positions
        this.nodeRenderer.updatePositions();
    }
    
    /**
     * Handle node drag start event
     * @param {Event} event - The drag event
     * @param {Object} node - The node being dragged
     */
    handleDragStart(event, node) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        node.fx = node.x;
        node.fy = node.y;
    }
    
    /**
     * Handle node drag event
     * @param {Event} event - The drag event
     * @param {Object} node - The node being dragged
     */
    handleDrag(event, node) {
        node.fx = event.x;
        node.fy = event.y;
    }
    
    /**
     * Handle node drag end event
     * @param {Event} event - The drag event
     * @param {Object} node - The node being dragged
     */
    handleDragEnd(event, node) {
        if (!event.active) this.simulation.alphaTarget(0);
        node.fx = null;
        node.fy = null;
    }
    
    /**
     * Update the graph with new data
     * @param {Object} graphData - New data for the graph
     */
    updateData(graphData) {
        // Store new data
        this.graphData = graphData;
        this.nodes = graphData.nodes || [];
        this.links = graphData.links || [];
        
        // Update renderers
        this.edgeRenderer.updateData(this.links);
        this.nodeRenderer.updateData(this.nodes);
        
        // Restart simulation
        this.simulation.nodes(this.nodes);
        this.simulation.force("link").links(this.links);
        this.simulation.alpha(1).restart();
    }
}
