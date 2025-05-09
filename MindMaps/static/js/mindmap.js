// Load JSON data from file data.json
d3.json("../static/data.json").then(function(graph) {
  const width = 1280;
  const height = 720;

  const svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

  // Set up the simulation with forces
  const simulation = d3.forceSimulation(graph.nodes)
    .force("link", d3.forceLink(graph.links)
                      .id(d => d.id)
                      .distance(150))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

  // Draw links (lines)
  const link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("class", "link");

  // Draw link labels
  const linkLabel = svg.append("g")
    .attr("class", "link-labels")
    .selectAll("text")
    .data(graph.links)
    .enter().append("text")
    .attr("class", "link-label")
    .attr("dy", -5)
    .text(d => d.label);

  // Draw nodes (circles)
  const node = svg.append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(graph.nodes)
    .enter().append("g")
    .attr("class", "node")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  node.append("circle")
    .attr("r", 20);

  // Draw node labels
  node.append("text")
    .attr("dy", 4)
    .attr("dx", 25)
    .text(d => d.id);

  // Update positions on each tick
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    linkLabel
      .attr("x", d => (d.source.x + d.target.x) / 2)
      .attr("y", d => (d.source.y + d.target.y) / 2);

    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  // Drag event handlers
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

}).catch(function(error) {
  console.error("Error loading data:", error);
});
