// an optional rendering parameters object
var renderingParams = {
    nodeRadius: 5,
    edgeThickness: 2
};

var nodeRenderingc0 = function(svg, data) {
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
            return 3;
        })
        .attr("fill", function(d) {
            return "red";
        })        
        .on("mouseover", function(d) {
            d3.select("#tooltip")
                .transition()		
                .duration(200)		
                .style("opacity", .9);		
            d3.select("#tooltip")
                .html(d.name)
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })					
        .on("mouseout", function(d) {		
            d3.select("#tooltip")
                .transition()
                .duration(500)		
                .style("opacity", 0);	
        });
};

var linkRenderingc0 = function(svg, data) {
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
        return d.y2;
    })          
    .attr("stroke-width", 2)
    .attr("stroke", "black");
}

var nodeRenderingc1 = function(svg, data) {
    // first level of clustering - render only level 1 meta nodes
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
        .attr("r", 3)
        .attr("fill", "blue")        
        .on("mouseover", function(d) {		
            d3.select("#tooltip")
                .transition()		
                .duration(200)		
                .style("opacity", .9);		
            d3.select("#tooltip")
                .html(d.name)
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })					
        .on("mouseout", function(d) {		
            d3.select("#tooltip")
                .transition()
                .duration(500)		
                .style("opacity", 0);	
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
    // second level of clustering - render only level 2 meta nodes
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
        .attr("r", 3)
        .attr("fill", "green");
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

module.exports = {
    nodeRenderingc0,
    linkRenderingc0,
    nodeRenderingc1,
    linkRenderingc1,
    nodeRenderingc2,
    linkRenderingc2,
    renderingParams
};
