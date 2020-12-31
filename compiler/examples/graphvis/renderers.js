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
    // one level of clustering - render only meta nodes
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
        .attr("r", 5)
        .attr("fill", "red");
};

var nodeRenderingc2 = function(svg, data) {
    // no clustering - render both meta nodes and individual nodes
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
        .attr("r", function(d) {
            if (d.isMetaNode)   return 5;
            else return 3;
        })
        .attr("fill", function(d) {
            if (d.isMetaNode) return "red";
            else return "blue";
        });
};

var linkRenderingc1 = function(svg, data) {
    // one level of clustering - render only meta edges
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
        //console.log("(", d.x1, ", ", d.y1, ") to (", d.x2, ", ", d.y2, ")");
        return d.y2;
    })          
    .attr("stroke-width", 3)
    .attr("stroke", "black");
}

var linkRenderingc2 = function(svg, data) {
    // no clustering - render only individual edges
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
        //console.log("(", d.x1, ", ", d.y1, ") to (", d.x2, ", ", d.y2, ")");
        return d.y2;
    })          
    .attr("stroke-width", 1)
    .attr("stroke", "black");
}

module.exports = {
    nodeRenderingc1,
    nodeRenderingc2,
    linkRenderingc1,
    linkRenderingc2,
    renderingParams,
    test
};
