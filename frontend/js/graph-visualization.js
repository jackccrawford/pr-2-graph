function createInteractiveGraph(graphData) {
    const width = 1200;
    const height = 800;
    
    const svg = d3.select("#graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#999");
    
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    
    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(30));
    
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graphData.edges)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke-width", d => Math.sqrt(d.properties.confidence * 5));
    
    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter().append("circle")
        .attr("class", d => `node ${d.type}`)
        .attr("r", d => {
            if (d.type === "participant") return 20;
            if (d.type === "breakthrough_moment") return 15;
            return 10;
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", showTooltip)
        .on("mouseout", hideTooltip);
    
    const labels = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(graphData.nodes)
        .enter().append("text")
        .text(d => d.label)
        .attr("font-size", "12px")
        .attr("dx", 25)
        .attr("dy", 4);
    
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
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
        } else if (d.type === "breakthrough_moment") {
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
