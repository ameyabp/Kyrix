// an optional rendering parameters object
var renderingParams = {
    nodeRadius: 5,
    edgeThickness: 2
};

var nodeRenderingc0 = function(svg, data) {
    // no clustering - render level 0 and level 1 nodes
    g = svg.append("g").attr("id", "nodeLayer0");
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
            //return d.memberNodeCount;
            return 3;
        })
        .attr("fill", function(d) {
            return "rgba(255, 0, 0, 0.7)";
        })
        .on("mouseover", function(d) {
            d3.select("#linkLayer0").selectAll("line")
                .filter(function(l) {
                    return l.edgeId.includes(d.nodeId);
                })
                .style("stroke", "rgba(0, 0, 0, 0.8)");
        })
        .on("mouseout", function(d) {
            d3.select("#linkLayer0").selectAll("line")
                .filter(function(l) {
                    return l.edgeId.includes(d.nodeId);
                })
                .style("stroke", "rgba(225, 225, 225, 0.5)");
        });
};

var linkRenderingc0 = function(svg, data) {
    // no clustering - render only individual edges (level 0)
    g = svg.append("g").attr("id", "linkLayer0");
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
    .attr("stroke-width", 1)
    .style("stroke", "rgba(225, 225, 225, 0.5)")
    .on("mouseover", function(d) {
        d3.select(this).style("stroke", "rgba(0, 0, 0, 0.8)");
    })
    .on("mouseout", function(d) {
        d3.select(this).style("stroke", "rgba(225, 225, 225, 0.5)");
    });
    //.attr("stroke", "black");
}

var nodeRenderingc1 = function(svg, data) {
    // first level of clustering - render nodes on cluster level 1 and 2
    g = svg.append("g").attr("id", "nodeLayer1");
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
            return Math.sqrt(d.memberNodeCount);
        })
        .attr("fill", function(d) {
            return "rgba(0, 0, 255, 0.7)";
        })
        .on("mouseover", function(d) {
            d3.select("#linkLayer1").selectAll("line")
                .filter(function(l) {
                    return l.edgeId.includes(d.nodeId);
                })
                .style("stroke", "rgba(0, 0, 0, 0.8)");
        })
        .on("mouseout", function(d) {
            d3.select("#linkLayer1").selectAll("line")
                .filter(function(l) {
                    return l.edgeId.includes(d.nodeId);
                })
                .style("stroke", "rgba(225, 225, 225, 0.5)");
        });
};

var linkRenderingc1 = function(svg, data) {
    // one level of clustering - render only level 1 meta edges
    g = svg.append("g").attr("id", "linkLayer1");
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
    .style("stroke", "rgba(225, 225, 225, 0.5)")
    .on("mouseover", function(d) {
        d3.select(this).style("stroke", "rgba(0, 0, 0, 0.8)");
    })
    .on("mouseout", function(d) {
        d3.select(this).style("stroke", "rgba(225, 225, 225, 0.5)");
    });
    //.attr("stroke", "black");
}

var nodeRenderingc2 = function(svg, data) {
    // second level of clustering - render nodes on cluster level 2 and 3
    g = svg.append("g").attr("id", "nodeLayer2");
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
            return Math.sqrt(d.memberNodeCount);
        })
        .attr("fill", function(d) {
            return "rgba(0, 255, 0, 0.85)";
        })
        .on("mouseover", function(d) {
            d3.select("#linkLayer2").selectAll("line")
                .filter(function(l) {
                    return l.edgeId.toString().includes(d.nodeId);
                })
                .style("stroke", "rgba(0, 0, 0, 0.8)");
        })
        .on("mouseout", function(d) {
            d3.select("#linkLayer2").selectAll("line")
                .filter(function(l) {
                    return l.edgeId.toString().includes(d.nodeId);
                })
                .style("stroke", "rgba(225, 225, 225, 0.5)");
        });
};

var linkRenderingc2 = function(svg, data) {
    // second level of clustering - render only level 2 meta edges
    g = svg.append("g").attr("id", "linkLayer2");
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
    .style("stroke", "rgba(225, 225, 225, 0.5)")
    .on("mouseover", function(d) {
        d3.select(this).style("stroke", "rgba(0, 0, 0, 0.8)");
    })
    .on("mouseout", function(d) {
        d3.select(this).style("stroke", "rgba(225, 225, 225, 0.5)");
    });
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
            return "rgba(198, 45, 225, 0.8)";
        });
};

var linkRenderingc3 = function(svg, data) {
    console.log(data);
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
