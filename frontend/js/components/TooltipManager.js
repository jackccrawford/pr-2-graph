/**
 * TooltipManager.js
 * Manages tooltips and detailed node/edge information display
 */
class TooltipManager {
    /**
     * Constructor for the tooltip manager
     * @param {Object} config - Configuration options
     * @param {Object} config.theme - Theme configuration
     */
    constructor(config = {}) {
        this.config = config;
        
        // Create tooltip element
        this.tooltip = d3.select("body")
            .append("div")
            .attr("class", "graph-tooltip")
            .style("position", "absolute")
            .style("background", "rgba(0,0,0,0.9)")
            .style("color", "white")
            .style("padding", "12px")
            .style("border-radius", "6px")
            .style("font-size", "13px")
            .style("box-shadow", "0 4px 14px rgba(0,0,0,0.5)")
            .style("border", "1px solid rgba(255,255,255,0.2)")
            .style("pointer-events", "none")
            .style("opacity", 0)
            .style("z-index", 1000)
            .style("max-width", "280px");
    }
    
    /**
     * Show tooltip with detailed information
     * @param {Event} event - Mouse event
     * @param {Object} d - Node or edge data
     */
    showTooltip(event, d) {
        // Generate tooltip content based on data type
        const content = this.generateTooltipContent(d);
        
        // Position and show tooltip with animation
        this.tooltip.transition()
            .duration(200)
            .style("opacity", .95);
            
        this.tooltip.html(content)
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 30) + "px");
    }
    
    /**
     * Hide tooltip
     */
    hideTooltip() {
        this.tooltip.transition()
            .duration(300)
            .style("opacity", 0);
    }
    
    /**
     * Generate tooltip HTML content based on node or edge data
     * @param {Object} data - Node or edge data
     * @returns {string} HTML content for tooltip
     */
    generateTooltipContent(data) {
        // Check if this is a node or an edge
        if (data.hasOwnProperty('source') && data.hasOwnProperty('target')) {
            return this.generateEdgeTooltip(data);
        } else {
            return this.generateNodeTooltip(data);
        }
    }
    
    /**
     * Generate tooltip content for a node
     * @param {Object} node - Node data
     * @returns {string} HTML content for tooltip
     */
    generateNodeTooltip(node) {
        const properties = node.properties || {};
        const typeIcons = {
            participant: '👤',
            issue: '🔴',
            solution: '🔵',
            breakthrough: '⚡',
            default: '🔹'
        };
        
        const icon = typeIcons[node.type] || typeIcons.default;
        
        let content = `
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px;">
                ${icon} ${node.label}
            </div>
            <div style="font-size: 12px; color: #ccc; margin-bottom: 10px;">
                Type: ${node.type.charAt(0).toUpperCase() + node.type.slice(1)}
            </div>
        `;
        
        // Add type-specific properties
        if (node.type === "participant") {
            content += this.addProperty('Role', properties.role);
            content += this.addProperty('Comments', properties.comment_count);
            content += this.addProperty('Influence', properties.influence, true);
        } else if (node.type === "issue") {
            content += this.addProperty('Author', properties.author);
            content += this.addProperty('Severity', properties.severity, true);
            content += this.addProperty('Status', properties.status);
            content += this.addProperty('Keywords', properties.keywords?.join(", "));
        } else if (node.type === "solution") {
            content += this.addProperty('Author', properties.author);
            content += this.addProperty('Complexity', properties.complexity, true);
            content += this.addProperty('Status', properties.status);
            content += this.addProperty('Keywords', properties.keywords?.join(", "));
        } else if (node.type === "breakthrough") {
            content += this.addProperty('Novelty', properties.novelty, true);
            content += this.addProperty('Impact', properties.impact, true);
            content += this.addProperty('Keywords', properties.keywords?.join(", "));
        }
        
        // Add "View Details" button styling (not functional in tooltip)
        content += `
            <div style="text-align: center; margin-top: 10px; font-size: 12px; color: #64B5F6; cursor: not-allowed;">
                Click for detailed view
            </div>
        `;
        
        return content;
    }
    
    /**
     * Generate tooltip content for an edge
     * @param {Object} edge - Edge data
     * @returns {string} HTML content for tooltip
     */
    generateEdgeTooltip(edge) {
        const properties = edge.properties || {};
        
        let content = `
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px;">
                🔗 ${edge.relationship}
            </div>
            <div style="font-size: 12px; margin-bottom: 10px;">
                <strong>From:</strong> ${edge.source.label || edge.source.id}<br>
                <strong>To:</strong> ${edge.target.label || edge.target.id}
            </div>
        `;
        
        // Add edge properties
        content += this.addProperty('Confidence', properties.confidence, true);
        content += this.addProperty('Context', properties.context);
        
        return content;
    }
    
    /**
     * Helper to format property display with progress bar for numeric values
     * @param {string} label - Property label
     * @param {any} value - Property value
     * @param {boolean} showBar - Whether to show a progress bar (for numeric values 0-1)
     * @returns {string} Formatted property HTML
     */
    addProperty(label, value, showBar = false) {
        if (value === undefined || value === null) {
            return '';
        }
        
        let progressBar = '';
        if (showBar && !isNaN(value) && value >= 0 && value <= 1) {
            // Create visual bar representation for values 0-1
            const percent = Math.round(value * 100);
            const barColor = this.getBarColor(value);
            progressBar = `
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 4px; margin-top: 3px; border-radius: 2px;">
                    <div style="width: ${percent}%; background: ${barColor}; height: 4px; border-radius: 2px;"></div>
                </div>
            `;
            value = (percent + '%');
        }
        
        return `
            <div style="margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #aaa;">${label}:</span>
                    <span style="font-weight: ${showBar ? 'bold' : 'normal'}">${value}</span>
                </div>
                ${progressBar}
            </div>
        `;
    }
    
    /**
     * Get appropriate color for progress bar based on value
     * @param {number} value - Value between 0 and 1
     * @returns {string} Color value
     */
    getBarColor(value) {
        if (value < 0.3) return '#FF5722'; // Low - Orange/Red
        if (value < 0.6) return '#FFC107'; // Medium - Amber
        return '#4CAF50'; // High - Green
    }
}
