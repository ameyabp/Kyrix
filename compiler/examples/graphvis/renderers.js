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
var nodeRenderingc1 = function(svg, data) {
    console.log("Rendering nodes");
    g = svg.append("g");
    g.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
            return d.x;
        })
        .attr("cy", function(d) {
            //console.log(d.y);
            return d.y;
            //return 1080;
        })
        .attr("r", 3)
        .attr("fill", "red");
};

var nodeRenderingc2 = function(svg, data) {
    console.log("Rendering nodes");
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
            //return 1080;
        })
        .attr("r", 3)
        .attr("fill", "red");
};

var linkRendering = function(svg, data) {
    console.log("Rendering links ", data);
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
        console.log("(", d.x1, ", ", d.y1, ") to (", d.x2, ", ", d.y2, ")");
        return d.y2;
    })          
    .attr("stroke-width", 1)
    .attr("stroke", "black");
}

module.exports = {
    nodeRenderingc1,
    nodeRenderingc2,
    linkRendering,
    renderingParams,
    test
};
