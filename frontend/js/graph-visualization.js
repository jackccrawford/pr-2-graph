function createInteractiveGraph(graphData) {
    // Clear any existing graph
    d3.select("#graph").selectAll("*").remove();
    
    const width = 1200;
    const height = 800;
    
    const svg = d3.select("#graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("background", "#0a0a0a")
        .style("border-radius", "8px");
    
    // Add arrow markers for directed edges
    svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#64b5f6");
    
    // Tooltip for node details
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "rgba(0,0,0,0.9)")
        .style("color", "white")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("font-size", "12px")
        .style("pointer-events", "none")
        .style("opacity", 0);
    
    // Use 'links' instead of 'edges' to match TIN Node Graph format
    const links = graphData.links || [];
    const nodes = graphData.nodes || [];
    
    // Color mapping for different node types
    const nodeColors = {
        participant: "#4CAF50",
        issue: "#FF5722", 
        solution: "#2196F3",
        breakthrough: "#FF9800",
        default: "#9E9E9E"
    };
    
    // Force simulation
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(150))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(35));
    
    // Create links
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke", "#64b5f6")
        .attr("stroke-width", 2)
        .attr("marker-end", "url(#arrowhead)");
    
    // Create link labels
    const linkLabel = svg.append("g")
        .attr("class", "link-labels")
        .selectAll("text")
        .data(links)
        .enter().append("text")
        .attr("class", "link-label")
        .attr("text-anchor", "middle")
        .attr("fill", "#90CAF9")
        .attr("font-size", "10px")
        .text(d => d.relationship);
    
    // Create nodes
    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("class", d => `node ${d.type}`)
        .attr("r", d => {
            if (d.type === "participant") return 25;
            if (d.type === "issue") return 20;
            if (d.type === "solution") return 20;
            if (d.type === "breakthrough") return 18;
            return 15;
        })
        .attr("fill", d => nodeColors[d.type] || nodeColors.default)
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", showTooltip)
        .on("mouseout", hideTooltip);
    
    // Create node labels
    const labels = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
        .text(d => d.type === 'participant' ? d.label : (d.label.length > 20 ? d.label.substring(0, 20) + '...' : d.label))
        .attr("font-size", "11px")
        .attr("fill", "white")
        .attr("text-anchor", "middle")
        .attr("dy", 4)
        .style("pointer-events", "none");
    
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        linkLabel
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);
        
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        
        labels
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
    
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    function showTooltip(event, d) {
        let content = `<strong>${d.label}</strong><br/>Type: ${d.type}<br/>`;
        
        if (d.type === "participant") {
            content += `Role: ${d.properties.role}<br/>Comments: ${d.properties.comment_count}`;
        } else if (d.type === "issue") {
            content += `Author: ${d.properties.author}<br/>`;
            content += `Severity: ${d.properties.severity}<br/>`;
            if (d.properties.keywords) {
                content += `Keywords: ${d.properties.keywords.join(", ")}`;
            }
        } else if (d.type === "solution") {
            content += `Author: ${d.properties.author}<br/>`;
            content += `Complexity: ${d.properties.complexity}<br/>`;
            if (d.properties.keywords) {
                content += `Keywords: ${d.properties.keywords.join(", ")}`;
            }
        } else if (d.type === "breakthrough") {
            content += `Novelty: ${d.properties.novelty}<br/>Impact: ${d.properties.impact}`;
        } else if (d.properties.keywords) {
            content += `Keywords: ${d.properties.keywords.join(", ")}`;
        }
        
        tooltip.transition().duration(200).style("opacity", .9);
        tooltip.html(content)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 28) + "px");
    }
    
    function hideTooltip() {
        tooltip.transition().duration(500).style("opacity", 0);
    }
}
