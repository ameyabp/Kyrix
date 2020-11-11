// an optional rendering parameters object
var renderingParams = {
    nodeRadius: 5,
    edgeThickness: 2
};

var test = function(svg, data, args) {
    console.log("test");
    console.log(data);
    var circle = svg.append("circle")
                    .attr("cx", 30)
                    .attr("cy", 30)
                    .attr("r", 20);

};

// rendering functions...
var nodeRendering = function(svg, data) {
    g = svg.append("g");
    g.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
            return d.x;
        })
        .attr("cy", function(d) {
            return d.y;
        })
        .attr("r", renderingParams.nodeRadius)
        .attr("fill", "red");
};

var linkRendering = function(svg, data) {
    g = svg.append("g");
    g.selectAll("line")
    .data(data)
    .enter()
    .append("line")
    .attr("x1", function(d) {
        return d.x1;
    })
    .attr("y1", function(d) {
        return d.y1;
    })
    .attr("x2", function(d) {
        return d.x2;
    })
    .attr("y2", function(d) {
        return d.y2;
    })          
    .attr("stroke-width", renderingParams.edgeThickness)
    .attr("stroke", "black");
}

module.exports = {
    nodeRendering,
    linkRendering,
    renderingParams,
    test
};
