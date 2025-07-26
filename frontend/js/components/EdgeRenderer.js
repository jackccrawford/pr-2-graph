/**
 * EdgeRenderer.js
 * Responsible for rendering and styling graph edges
 */
class EdgeRenderer {
    /**
     * Constructor for the edge renderer
     * @param {Object} config - Configuration options
     * @param {Object} config.svg - D3 SVG element
     * @param {Array} config.links - Link data array
     * @param {Object} config.theme - Theme configuration
     */
    constructor(config) {
        this.svg = config.svg;
        this.links = config.links;
        this.theme = config.theme;
        
        // D3 selections
        this.linkElements = null;
        this.linkLabelElements = null;
        
        // Initialize
        this.initialize();
    }
    
    /**
     * Initialize the edge renderer
     */
    initialize() {
        // Add arrow markers for directed edges
        this.setupArrowMarker();
        
        // Create links
        this.linkElements = this.svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(this.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke", this.theme.linkColor)
            .attr("stroke-width", d => this.getLinkWidth(d))
            .attr("stroke-opacity", d => this.getLinkOpacity(d))
            .attr("marker-end", "url(#arrowhead)");
        
        // Create link labels
        this.linkLabelElements = this.svg.append("g")
            .attr("class", "link-labels")
            .selectAll("text")
            .data(this.links)
            .enter().append("text")
            .attr("class", "link-label")
            .attr("text-anchor", "middle")
            .attr("fill", this.theme.linkLabelColor)
            .attr("font-size", "10px")
            .text(d => d.relationship);
    }
    
    /**
     * Setup arrow marker for directed edges
     */
    setupArrowMarker() {
        this.svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 25)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", this.theme.linkColor);
    }
    
    /**
     * Get appropriate stroke width based on link properties
     * @param {Object} link - The link to get width for
     * @returns {number} The stroke width
     */
    getLinkWidth(link) {
        // Base width
        let width = 2;
        
        // Adjust based on confidence if available
        if (link.properties && link.properties.confidence) {
            // Scale between 1 and 4 based on confidence (0-1)
            width = 1 + (link.properties.confidence * 3);
        }
        
        return width;
    }
    
    /**
     * Get appropriate opacity based on link properties
     * @param {Object} link - The link to get opacity for
     * @returns {number} The opacity value
     */
    getLinkOpacity(link) {
        // Default opacity
        let opacity = 0.8;
        
        // Adjust based on confidence if available
        if (link.properties && link.properties.confidence) {
            // Scale between 0.4 and 1.0 based on confidence (0-1)
            opacity = 0.4 + (link.properties.confidence * 0.6);
        }
        
        return opacity;
    }
    
    /**
     * Update link positions during simulation
     */
    updatePositions() {
        this.linkElements
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        this.linkLabelElements
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);
    }
    
    /**
     * Update with new data
     * @param {Array} links - New link data array
     */
    updateData(links) {
        this.links = links;
        
        // Remove old elements
        this.linkElements.remove();
        this.linkLabelElements.remove();
        
        // Reinitialize with new data
        this.initialize();
    }
}
