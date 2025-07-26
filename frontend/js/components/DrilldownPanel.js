/**
 * DrilldownPanel.js
 * Provides detailed exploration of graph nodes and relationships
 */
class DrilldownPanel {
    /**
     * Constructor for the drilldown panel
     * @param {Object} config - Configuration options
     * @param {string} config.containerId - ID of the container element
     * @param {Object} config.theme - Theme configuration
     */
    constructor(config = {}) {
        this.config = {
            containerId: 'drilldown-panel',
            theme: {
                background: 'rgba(20, 20, 20, 0.95)',
                textColor: '#ffffff',
                accentColor: '#64b5f6'
            },
            ...config
        };
        
        // State
        this.isVisible = false;
        this.currentItem = null;
        this.relatedNodes = [];
        this.relatedLinks = [];
        
        // Initialize panel
        this.initialize();
    }
    
    /**
     * Initialize the drilldown panel
     */
    initialize() {
        // Create panel element if it doesn't exist
        if (!document.getElementById(this.config.containerId)) {
            const panel = document.createElement('div');
            panel.id = this.config.containerId;
            panel.className = 'drilldown-panel';
            panel.style.position = 'absolute';
            panel.style.right = '20px';
            panel.style.top = '80px';
            panel.style.width = '320px';
            panel.style.maxHeight = 'calc(100vh - 120px)';
            panel.style.backgroundColor = this.config.theme.background;
            panel.style.color = this.config.theme.textColor;
            panel.style.borderRadius = '8px';
            panel.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
            panel.style.padding = '15px';
            panel.style.display = 'none';
            panel.style.zIndex = '1000';
            panel.style.overflowY = 'auto';
            panel.style.border = '1px solid rgba(255, 255, 255, 0.1)';
            
            // Add close button
            const closeButton = document.createElement('div');
            closeButton.className = 'close-button';
            closeButton.innerHTML = '×';
            closeButton.style.position = 'absolute';
            closeButton.style.right = '12px';
            closeButton.style.top = '10px';
            closeButton.style.fontSize = '24px';
            closeButton.style.cursor = 'pointer';
            closeButton.style.color = 'rgba(255, 255, 255, 0.7)';
            closeButton.addEventListener('click', () => this.hide());
            
            panel.appendChild(closeButton);
            
            // Add content container
            const content = document.createElement('div');
            content.className = 'drilldown-content';
            panel.appendChild(content);
            
            document.body.appendChild(panel);
        }
        
        // Initialize panel contents
        this.panel = document.getElementById(this.config.containerId);
        this.contentContainer = this.panel.querySelector('.drilldown-content');
    }
    
    /**
     * Show the drilldown panel with details for a node
     * @param {Object} node - Node data
     * @param {Array} allNodes - All nodes in the graph
     * @param {Array} allLinks - All links in the graph
     */
    showNode(node, allNodes, allLinks) {
        // Store current item
        this.currentItem = node;
        
        // Find related nodes and links
        this.findRelatedItems(node, allNodes, allLinks);
        
        // Generate content
        this.contentContainer.innerHTML = this.generateNodeContent(node);
        
        // Show panel
        this.show();
    }
    
    /**
     * Show the drilldown panel with details for an edge
     * @param {Object} link - Link data
     */
    showLink(link) {
        // Store current item
        this.currentItem = link;
        
        // Generate content
        this.contentContainer.innerHTML = this.generateLinkContent(link);
        
        // Show panel
        this.show();
    }
    
    /**
     * Show the panel
     */
    show() {
        this.panel.style.display = 'block';
        this.isVisible = true;
    }
    
    /**
     * Hide the panel
     */
    hide() {
        this.panel.style.display = 'none';
        this.isVisible = false;
        this.currentItem = null;
    }
    
    /**
     * Find nodes and links related to the selected node
     * @param {Object} node - The selected node
     * @param {Array} allNodes - All nodes in the graph
     * @param {Array} allLinks - All links in the graph
     */
    findRelatedItems(node, allNodes, allLinks) {
        // Clear previous related items
        this.relatedNodes = [];
        this.relatedLinks = [];
        
        // Find links connected to this node
        this.relatedLinks = allLinks.filter(link => 
            link.source.id === node.id || link.target.id === node.id
        );
        
        // Find nodes connected to this node
        const connectedNodeIds = new Set();
        this.relatedLinks.forEach(link => {
            if (link.source.id === node.id) {
                connectedNodeIds.add(link.target.id);
            } else {
                connectedNodeIds.add(link.source.id);
            }
        });
        
        this.relatedNodes = allNodes.filter(n => connectedNodeIds.has(n.id));
    }
    
    /**
     * Generate detailed HTML content for a node
     * @param {Object} node - Node data
     * @returns {string} HTML content
     */
    generateNodeContent(node) {
        const properties = node.properties || {};
        
        // Type-specific icons
        const typeIcons = {
            participant: '👤',
            issue: '🔴',
            solution: '🔵',
            breakthrough: '⚡',
            default: '🔹'
        };
        
        const icon = typeIcons[node.type] || typeIcons.default;
        const nodeTypeFormatted = node.type.charAt(0).toUpperCase() + node.type.slice(1);
        
        // Header section
        let content = `
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 20px;">${icon}</div>
                <h2 style="margin: 10px 0; font-size: 18px;">${node.label}</h2>
                <div style="display: inline-block; padding: 3px 12px; border-radius: 12px; 
                     background: ${this.getNodeTypeColor(node.type)}; font-size: 12px;">
                    ${nodeTypeFormatted}
                </div>
            </div>
            <div class="separator" style="height: 1px; background: rgba(255,255,255,0.1); margin: 15px 0;"></div>
        `;
        
        // Properties section
        content += '<div style="margin-bottom: 20px;">';
        content += '<h3 style="font-size: 14px; color: #BBB; margin-bottom: 12px;">Properties</h3>';
        
        // Add type-specific properties with styling
        if (node.type === "participant") {
            content += this.addDetailProperty('Role', properties.role);
            content += this.addDetailProperty('Comments', properties.comment_count);
            content += this.addDetailProperty('Influence', properties.influence, true);
            content += this.addDetailProperty('Activity Level', properties.activity_level, true);
            content += this.addDetailProperty('First Contribution', properties.first_contribution);
            content += this.addDetailProperty('Last Contribution', properties.last_contribution);
        } else if (node.type === "issue") {
            content += this.addDetailProperty('Author', properties.author);
            content += this.addDetailProperty('Severity', properties.severity, true);
            content += this.addDetailProperty('Status', properties.status);
            content += this.addDetailProperty('Priority', properties.priority, true);
            content += this.addDetailProperty('Identified At', properties.timestamp);
            content += this.addDetailProperty('Keywords', properties.keywords?.join(", "));
        } else if (node.type === "solution") {
            content += this.addDetailProperty('Author', properties.author);
            content += this.addDetailProperty('Complexity', properties.complexity, true);
            content += this.addDetailProperty('Status', properties.status);
            content += this.addDetailProperty('Implementation Time', properties.implementation_time);
            content += this.addDetailProperty('Proposed At', properties.timestamp);
            content += this.addDetailProperty('Keywords', properties.keywords?.join(", "));
        } else if (node.type === "breakthrough") {
            content += this.addDetailProperty('Novelty', properties.novelty, true);
            content += this.addDetailProperty('Impact', properties.impact, true);
            content += this.addDetailProperty('Discovered At', properties.timestamp);
            content += this.addDetailProperty('Keywords', properties.keywords?.join(", "));
        }
        
        content += '</div>';
        
        // Related nodes section
        content += '<div class="separator" style="height: 1px; background: rgba(255,255,255,0.1); margin: 15px 0;"></div>';
        content += `<h3 style="font-size: 14px; color: #BBB; margin-bottom: 12px;">Relationships (${this.relatedNodes.length})</h3>`;
        
        if (this.relatedNodes.length > 0) {
            content += '<div style="max-height: 200px; overflow-y: auto;">';
            
            this.relatedLinks.forEach((link, i) => {
                const isOutgoing = link.source.id === node.id;
                const relatedNode = isOutgoing ? link.target : link.source;
                const direction = isOutgoing ? 'to' : 'from';
                
                content += `
                    <div style="padding: 8px; background: rgba(255,255,255,0.05); margin-bottom: 8px; border-radius: 4px;">
                        <div style="display: flex; align-items: center;">
                            <div style="width: 8px; height: 8px; border-radius: 50%; 
                                 background: ${this.getNodeTypeColor(relatedNode.type)}; margin-right: 6px;"></div>
                            <span style="font-size: 13px;">${relatedNode.label}</span>
                        </div>
                        <div style="font-size: 12px; color: #BBB; margin-top: 4px; display: flex; align-items: center;">
                            <span style="color: #64B5F6; margin: 0 4px;">
                                ${isOutgoing ? '→' : '←'} ${link.relationship}
                            </span>
                            <span>(${direction} ${relatedNode.type})</span>
                        </div>
                    </div>
                `;
            });
            
            content += '</div>';
        } else {
            content += '<p style="color: #999; font-size: 13px;">No relationships found</p>';
        }
        
        return content;
    }
    
    /**
     * Generate detailed HTML content for a link
     * @param {Object} link - Link data
     * @returns {string} HTML content
     */
    generateLinkContent(link) {
        const properties = link.properties || {};
        
        // Header section
        let content = `
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 24px;">🔗</div>
                <h2 style="margin: 10px 0; font-size: 18px;">${link.relationship}</h2>
            </div>
            <div class="separator" style="height: 1px; background: rgba(255,255,255,0.1); margin: 15px 0;"></div>
        `;
        
        // Connection details
        content += `
            <div style="margin-bottom: 20px;">
                <h3 style="font-size: 14px; color: #BBB; margin-bottom: 12px;">Connection</h3>
                
                <div style="display: flex; margin-bottom: 12px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; 
                         background: ${this.getNodeTypeColor(link.source.type)}; margin: 5px 8px 0 0;"></div>
                    <div>
                        <div style="font-size: 14px;">${link.source.label || link.source.id}</div>
                        <div style="font-size: 12px; color: #BBB;">${link.source.type}</div>
                    </div>
                </div>
                
                <div style="text-align: center; padding: 5px; font-size: 20px; color: #64B5F6;">↓</div>
                
                <div style="display: flex;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; 
                         background: ${this.getNodeTypeColor(link.target.type)}; margin: 5px 8px 0 0;"></div>
                    <div>
                        <div style="font-size: 14px;">${link.target.label || link.target.id}</div>
                        <div style="font-size: 12px; color: #BBB;">${link.target.type}</div>
                    </div>
                </div>
            </div>
        `;
        
        // Properties section
        content += '<div class="separator" style="height: 1px; background: rgba(255,255,255,0.1); margin: 15px 0;"></div>';
        content += '<h3 style="font-size: 14px; color: #BBB; margin-bottom: 12px;">Properties</h3>';
        content += '<div style="margin-bottom: 20px;">';
        
        // Add link properties
        content += this.addDetailProperty('Confidence', properties.confidence, true);
        content += this.addDetailProperty('Established At', properties.timestamp);
        content += this.addDetailProperty('Context', properties.context);
        content += this.addDetailProperty('Source', properties.source);
        
        content += '</div>';
        
        return content;
    }
    
    /**
     * Add a detailed property with optional progress bar
     * @param {string} label - Property label
     * @param {any} value - Property value
     * @param {boolean} showBar - Whether to show a progress bar
     * @returns {string} Property HTML
     */
    addDetailProperty(label, value, showBar = false) {
        if (value === undefined || value === null) {
            return '';
        }
        
        let progressBar = '';
        if (showBar && !isNaN(value) && value >= 0 && value <= 1) {
            // Create visual bar representation
            const percent = Math.round(value * 100);
            const barColor = this.getBarColor(value);
            progressBar = `
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 6px; margin-top: 6px; border-radius: 3px;">
                    <div style="width: ${percent}%; background: ${barColor}; height: 6px; border-radius: 3px;"></div>
                </div>
                <div style="text-align: right; font-size: 12px; margin-top: 2px;">${percent}%</div>
            `;
            value = '';
        }
        
        return `
            <div style="margin-bottom: 12px;">
                <div style="font-size: 13px; color: #999; margin-bottom: 4px;">${label}</div>
                <div style="font-size: ${showBar ? '14px' : '14px'}; ${showBar ? 'font-weight: bold;' : ''}">
                    ${value}
                </div>
                ${progressBar}
            </div>
        `;
    }
    
    /**
     * Get color for node type
     * @param {string} type - Node type
     * @returns {string} Color value
     */
    getNodeTypeColor(type) {
        const nodeColors = {
            participant: "#4CAF50",
            issue: "#FF5722", 
            solution: "#2196F3",
            breakthrough: "#FF9800",
            default: "#9E9E9E"
        };
        
        return nodeColors[type] || nodeColors.default;
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
