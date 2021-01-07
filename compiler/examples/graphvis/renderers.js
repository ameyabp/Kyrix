// an optional rendering parameters object
var renderingParams = {
    nodeRadius: 5,
    edgeThickness: 2
};

var nodeRenderingc0 = function(svg, data) {
    // no clustering - render level 0 and level 1 nodes
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
            if (d.clusterLevel == 0)
                return 3;
            else
                return 4;
        })
        .attr("fill", function(d) {
            if (d.clusterLevel == 0)
                return "red";
            else
                return "blue";
        });
};

var linkRenderingc0 = function(svg, data) {
    // no clustering - render only individual edges (level 0)
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
    .attr("stroke-width", 2)
    .attr("stroke", "black");
}

var nodeRenderingc1 = function(svg, data) {
    // first level of clustering - render nodes on cluster level 1 and 2
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
            if (d.clusterLevel == 1)
                return 3;
            else
                return 4;
        })
        .attr("fill", function(d) {
            if (d.clusterLevel == 1)
                return "blue";
            else
                return "green";
        });
};

var linkRenderingc1 = function(svg, data) {
    // one level of clustering - render only level 1 meta edges
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
    .attr("stroke-width", 2)
    .attr("stroke", "black");
}

var nodeRenderingc2 = function(svg, data) {
    // second level of clustering - render nodes on cluster level 2 and 3
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
            if (d.clusterLevel == 2)
                return 3;
            else
                return 4;
        })
        .attr("fill", function(d) {
            if (d.clusterLevel == 2)
                return "green";
            else
                return "rgba(198, 45, 205, 0.8)";
        });
};

var linkRenderingc2 = function(svg, data) {
    // second level of clustering - render only level 2 meta edges
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
    .attr("stroke-width", 2)
    .attr("stroke", "black");
}
var nodeRenderingc3 = function(svg, data) {
    // second level of clustering - render only level 3 meta nodes
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
            return 3;
        })
        .attr("fill", function(d) {
            return "rgba(198, 45, 205, 0.8)";
        });
};

var linkRenderingc3 = function(svg, data) {
    // second level of clustering - render only level 3 meta edges
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
    .attr("stroke-width", 2)
    .attr("stroke", "black");
}

module.exports = {
    nodeRenderingc0,
    linkRenderingc0,
    nodeRenderingc1,
    linkRenderingc1,
    nodeRenderingc2,
    linkRenderingc2,
    nodeRenderingc3,
    linkRenderingc3,
    renderingParams
};
