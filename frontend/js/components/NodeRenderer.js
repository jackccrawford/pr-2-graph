/**
 * NodeRenderer.js
 * Responsible for rendering and styling graph nodes
 */
class NodeRenderer {
    /**
     * Constructor for the node renderer
     * @param {Object} config - Configuration options
     * @param {Object} config.svg - D3 SVG element
     * @param {Array} config.nodes - Node data array
     * @param {Object} config.theme - Theme configuration
     * @param {Object} config.tooltipManager - Tooltip manager instance
     * @param {Function} config.onDragStart - Drag start event handler
     * @param {Function} config.onDrag - Drag event handler
     * @param {Function} config.onDragEnd - Drag end event handler
     */
    constructor(config) {
        this.svg = config.svg;
        this.nodes = config.nodes;
        this.theme = config.theme;
        this.tooltipManager = config.tooltipManager;
        this.onDragStart = config.onDragStart;
        this.onDrag = config.onDrag;
        this.onDragEnd = config.onDragEnd;
        
        // Node styling
        this.nodeColors = {
            participant: "#4CAF50",
            issue: "#FF5722", 
            solution: "#2196F3",
            breakthrough: "#FF9800",
            default: "#9E9E9E"
        };
        
        // D3 selections
        this.nodeElements = null;
        this.labelElements = null;
        
        // Initialize the node renderer
        this.initialize();
    }
    
    /**
     * Initialize the node renderer
     */
    initialize() {
        // Create nodes
        this.nodeElements = this.svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(this.nodes)
            .enter().append("circle")
            .attr("class", d => `node ${d.type}`)
            .attr("r", d => this.getNodeRadius(d))
            .attr("fill", d => this.getNodeColor(d))
            .attr("stroke", this.theme.nodeStroke)
            .attr("stroke-width", 2)
            .call(d3.drag()
                .on("start", (event, d) => this.onDragStart(event, d))
                .on("drag", (event, d) => this.onDrag(event, d))
                .on("end", (event, d) => this.onDragEnd(event, d)))
            .on("mouseover", (event, d) => this.tooltipManager.showTooltip(event, d))
            .on("mouseout", () => this.tooltipManager.hideTooltip());
        
        // Create node labels
        this.labelElements = this.svg.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(this.nodes)
            .enter().append("text")
            .text(d => this.getLabelText(d))
            .attr("font-size", "11px")
            .attr("fill", "white")
            .attr("text-anchor", "middle")
            .attr("dy", 4)
            .style("pointer-events", "none");
    }
    
    /**
     * Get the radius for a node based on type and importance
     * @param {Object} node - The node to get radius for
     * @returns {number} The radius value
     */
    getNodeRadius(node) {
        // Base sizes
        const baseSizes = {
            participant: 25,
            issue: 20,
            solution: 20,
            breakthrough: 18,
            default: 15
        };
        
        // Get base size for node type
        let radius = baseSizes[node.type] || baseSizes.default;
        
        // Apply importance scaling if available
        if (node.properties && node.properties.importance) {
            // Scale between 0.8 and 1.5 times base size
            const scale = 0.8 + (node.properties.importance * 0.7);
            radius *= scale;
        }
        
        return radius;
    }
    
    /**
     * Get the fill color for a node
     * @param {Object} node - The node to get color for
     * @returns {string} The color value
     */
    getNodeColor(node) {
        return this.nodeColors[node.type] || this.nodeColors.default;
    }
    
    /**
     * Get the display text for a node label
     * @param {Object} node - The node to get label for
     * @returns {string} The label text
     */
    getLabelText(node) {
        if (node.type === 'participant') {
            return node.label;
        }
        
        // Truncate long labels
        return node.label.length > 20 
            ? node.label.substring(0, 20) + '...' 
            : node.label;
    }
    
    /**
     * Update node positions during simulation
     */
    updatePositions() {
        this.nodeElements
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        
        this.labelElements
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    }
    
    /**
     * Update with new data
     * @param {Array} nodes - New node data array
     */
    updateData(nodes) {
        this.nodes = nodes;
        
        // Remove old elements
        this.nodeElements.remove();
        this.labelElements.remove();
        
        // Reinitialize with new data
        this.initialize();
    }
}
