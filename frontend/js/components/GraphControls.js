/**
 * GraphControls.js
 * Interactive controls for the knowledge graph visualization
 */
class GraphControls {
    /**
     * Constructor for the graph controls
     * @param {Object} config - Configuration options
     * @param {Object} config.graphManager - Reference to the GraphManager
     * @param {string} config.containerId - ID of the container element
     */
    constructor(config = {}) {
        this.config = {
            containerId: 'graph',
            controlsId: 'graph-controls',
            ...config
        };
        
        this.graphManager = config.graphManager;
        if (!this.graphManager) {
            console.error("GraphControls requires a GraphManager instance");
        }
        
        // Initialize the controls
        this.initialize();
    }
    
    /**
     * Initialize the graph controls
     */
    initialize() {
        // Create controls container if it doesn't exist
        const container = document.getElementById(this.config.containerId);
        let controlsDiv = document.getElementById(this.config.controlsId);
        
        if (!controlsDiv) {
            controlsDiv = document.createElement('div');
            controlsDiv.id = this.config.controlsId;
            controlsDiv.className = 'graph-controls';
            container.appendChild(controlsDiv);
        }
        
        // Store reference to controls container
        this.controlsContainer = controlsDiv;
        
        // Add controls
        this.createZoomControls();
        this.createFilterControls();
        this.createLayoutControls();
    }
    
    /**
     * Create zoom controls
     */
    createZoomControls() {
        const zoomControls = document.createElement('div');
        zoomControls.className = 'zoom-controls';
        
        // Zoom in button
        const zoomInBtn = document.createElement('button');
        zoomInBtn.textContent = '+ Zoom In';
        zoomInBtn.addEventListener('click', () => this.handleZoom('in'));
        
        // Zoom out button
        const zoomOutBtn = document.createElement('button');
        zoomOutBtn.textContent = '- Zoom Out';
        zoomOutBtn.addEventListener('click', () => this.handleZoom('out'));
        
        // Reset zoom button
        const resetZoomBtn = document.createElement('button');
        resetZoomBtn.textContent = 'Reset View';
        resetZoomBtn.addEventListener('click', () => this.handleZoom('reset'));
        
        // Add buttons to controls
        zoomControls.appendChild(zoomInBtn);
        zoomControls.appendChild(zoomOutBtn);
        zoomControls.appendChild(resetZoomBtn);
        
        this.controlsContainer.appendChild(zoomControls);
    }
    
    /**
     * Create filter controls
     */
    createFilterControls() {
        const filterControls = document.createElement('div');
        filterControls.className = 'filter-controls';
        
        // Filter by node type dropdown
        const filterSelect = document.createElement('select');
        filterSelect.className = 'filter-select';
        
        // Add options
        const options = [
            { value: 'all', label: 'All Types' },
            { value: 'participant', label: 'Participants' },
            { value: 'issue', label: 'Issues' },
            { value: 'solution', label: 'Solutions' },
            { value: 'breakthrough', label: 'Breakthroughs' }
        ];
        
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.value;
            opt.textContent = option.label;
            filterSelect.appendChild(opt);
        });
        
        // Add event listener
        filterSelect.addEventListener('change', (event) => {
            this.handleFilter(event.target.value);
        });
        
        filterControls.appendChild(filterSelect);
        this.controlsContainer.appendChild(filterControls);
    }
    
    /**
     * Create layout controls
     */
    createLayoutControls() {
        const layoutControls = document.createElement('div');
        layoutControls.className = 'layout-controls';
        
        // Toggle physics button
        const togglePhysicsBtn = document.createElement('button');
        togglePhysicsBtn.textContent = 'Toggle Physics';
        togglePhysicsBtn.addEventListener('click', () => this.handleTogglePhysics());
        
        // Rearrange button
        const rearrangeBtn = document.createElement('button');
        rearrangeBtn.textContent = 'Rearrange';
        rearrangeBtn.addEventListener('click', () => this.handleRearrange());
        
        // Add buttons to controls
        layoutControls.appendChild(togglePhysicsBtn);
        layoutControls.appendChild(rearrangeBtn);
        
        this.controlsContainer.appendChild(layoutControls);
    }
    
    /**
     * Handle zoom control
     * @param {string} direction - Direction to zoom: 'in', 'out', or 'reset'
     */
    handleZoom(direction) {
        // Implementation will be added when we add zoom capabilities
        console.log(`Zoom ${direction} clicked`);
        
        // For now, just log the action
        if (direction === 'in') {
            // Future: Apply zoom in transformation
        } else if (direction === 'out') {
            // Future: Apply zoom out transformation
        } else if (direction === 'reset') {
            // Future: Reset zoom to default
        }
    }
    
    /**
     * Handle filter selection
     * @param {string} filterValue - Filter value
     */
    handleFilter(filterValue) {
        console.log(`Filter selected: ${filterValue}`);
        
        // Get all node elements
        const nodeElements = d3.select(`#${this.config.containerId}`)
            .selectAll(".nodes circle");
        
        // Apply filter
        if (filterValue === 'all') {
            // Show all nodes
            nodeElements.style("opacity", 1);
        } else {
            // Filter by type
            nodeElements.style("opacity", d => d.type === filterValue ? 1 : 0.2);
        }
    }
    
    /**
     * Handle toggle physics
     */
    handleTogglePhysics() {
        console.log("Toggle physics clicked");
        
        if (this.graphManager && this.graphManager.graphViz) {
            const simulation = this.graphManager.graphViz.simulation;
            
            if (simulation.alpha() > 0) {
                // Physics is active, stop it
                simulation.alpha(0).stop();
            } else {
                // Physics is inactive, restart it
                simulation.alpha(0.3).restart();
            }
        }
    }
    
    /**
     * Handle rearrange layout
     */
    handleRearrange() {
        console.log("Rearrange clicked");
        
        if (this.graphManager && this.graphManager.graphViz) {
            const simulation = this.graphManager.graphViz.simulation;
            
            // Restart simulation with high alpha to reorganize
            simulation.alpha(0.8).restart();
        }
    }
}
