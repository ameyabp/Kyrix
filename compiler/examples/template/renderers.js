// an optional rendering parameters object
var renderingParams = {};

// rendering functions...

var test = function(svg, data, args) {
    console.log("test");
    console.log(data);
    var circle = svg.append("circle")
                    .attr("cx", 30)
                    .attr("cy", 30)
                    .attr("r", 20);

};

module.exports = {
    renderingParams,
    test
};
