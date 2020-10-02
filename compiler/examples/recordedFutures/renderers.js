// an optional rendering parameters object
var renderingParams = {
    stateScaleRange: 300000,
    stateScaleStep: 40000
};

var test = function(svg, data, args) {
    console.log(data);
};

// rendering functions...
var stateMapRendering = function(svg, data, args) {
    console.log(data);
    g = svg.append("g");
    var params = args.renderingParams;

    var projection = d3
        .geoMercator()
        .translate([3201.4222222222224, 1479.8808343133628])
        .scale((1 << 13) / 2 / Math.PI);
    var path = d3.geoPath().projection(projection);

    var color = d3
        .scaleThreshold()
        .domain(d3.range(0, params.stateScaleRange, params.stateScaleStep))
        .range(d3.schemeYlOrRd[9]);

    var filteredData = [];
    for (var j = 0; j < data.length; j++) {
        if (data[j].year == params.fire_year) {
            data[j].geomstr = params.geomstrs[data[j].state];
            filteredData.push(data[j]);
        }
    }

    g.selectAll("path")
        .data(filteredData)
        .enter()
        .append("path")
        .attr("d", function(d) {
            var feature = JSON.parse(d.geomstr);
            return path(feature);
        })
        .style("stroke", "#fff")
        .style("stroke-width", "0.5")
        .style("fill", function(d) {
            return color(+d.total_fire_size);
        });
};

module.exports = {
    stateMapRendering,
    renderingParams,
    test
};
