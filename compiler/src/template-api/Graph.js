const getBodyStringOfFunction = require("./Utilities").getBodyStringOfFunction;
const formatAjvErrorMessage = require("./Utilities").formatAjvErrorMessage;
const fs = require("fs");
const cloneDeep = require("lodash.clonedeep");

/**
 * Constructor of a Graph object
 * @param args
 * @constructor
 */
function Graph(args_) {
    // verify against schema
    // defaults are assigned at the same time
    var args = cloneDeep(args_);
    var schema = JSON.parse(
        fs.readFileSync("../../src/template-api/json-schema/Graph.json")
    );
    // ajv is a fast json schema validator
    var ajv = new require("ajv")({useDefaults: true});
    ajv.addKeyword("typeofFunction", {
        compile: () => data => data instanceof Function
    });
    var validator = ajv.compile(schema);
    var valid = validator(args);
    if (!valid)
        throw new Error(
            "Constructing Graph: " + formatAjvErrorMessage(validator.errors[0])
        );

    this.numClusters = args.marks.cluster.numClusters;

    console.log("----SUCCESS validating json schema----");
}

// get rendering function for an SSV layer based on cluster mode
function getLayerRenderer() {
    function renderCircleBody() {
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        params.processClusterAgg(data, params);

        // set up d3.scale for circle/text size
        var agg;
        var curMeasure = params.aggMeasures[0];
        agg = curMeasure.function + "(" + curMeasure.field + ")";
        var minDomain = params[args.ssvId + "_" + agg + "_min"];
        var maxDomain = params[args.ssvId + "_" + agg + "_max"];
        var circleSizeInterpolator = d3
            .scaleSqrt()
            .domain([minDomain, maxDomain])
            .range([params.circleMinSize, params.circleMaxSize]);

        // append circles & text
        var g = svg.append("g").classed("hovercircle", true);
        g.style("opacity", 0);
        g.selectAll("circle")
            .data(data)
            .enter()
            .append("circle")
            .attr("r", function(d) {
                return circleSizeInterpolator(d.clusterAgg[agg]);
            })
            .attr("cx", function(d) {
                return d.cx;
            })
            .attr("cy", function(d) {
                return d.cy;
            })
            .style("fill-opacity", 0.5)
            //            .attr("fill", "honeydew")
            .attr("fill", "#d7dbff")
            //            .attr("stroke", "#ADADAD")
            //            .style("stroke-width", "1px")
            .style("pointer-events", "fill")
            .classed("kyrix-retainsizezoom", true);
        g.selectAll("text")
            .data(data)
            .enter()
            .append("text")
            .attr("dy", "0.3em")
            .text(function(d) {
                return d3.format(params.numberFormat)(+d.clusterAgg[agg]);
            })
            .attr("font-size", function(d) {
                return circleSizeInterpolator(d.clusterAgg[agg]) / 2;
            })
            .attr("x", function(d) {
                return d.cx;
            })
            .attr("y", function(d) {
                return d.cy;
            })
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .style("fill-opacity", 1)
            //            .style("fill", "navy")
            .style("fill", "#0f00d0")
            .style("pointer-events", "none")
            .classed("kyrix-retainsizezoom", true)
            .each(function(d) {
                params.textwrap(
                    d3.select(this),
                    circleSizeInterpolator(d.clusterAgg[agg]) * 1.5
                );
            });

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        var hoverSelector = "circle";
    }

    function renderObjectClusterNumBody() {
        var g = svg.select("g:last-of-type");
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        g.selectAll(".clusternum")
            .data(data)
            .enter()
            .append("text")
            .text(function(d) {
                return d3.format(
                    params.numberFormat
                )(+JSON.parse(d.clusterAgg)["count(*)"]);
            })
            .attr("x", function(d) {
                return +d.cx;
            })
            .attr("y", function(d) {
                // TODO: y offset needs to be exposed as a parameter
                //return +d.miny + 13;
                return +d.cy + sizeScale(d.fire_size) * 0.2;
            })
            .attr("dy", ".35em")
            .attr("font-size", d => 18 + (3 * sizeScale(d.fire_size)) / 50)
            .attr("text-anchor", "middle")
            //.attr("fill", "#f47142")
            .attr("fill", "#8c7573")
            .style("fill-opacity", 1)
            .classed("kyrix-retainsizezoom", true);
    }

    function renderContourBody() {
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        var roughN = params.roughN;
        var bandwidth = params.contourBandwidth;
        var radius = params.contourRadius;
        var decayRate = 2.4;
        var cellSize = 2;
        var contourWidth, contourHeight, x, y;
        if ("tileX" in args) {
            // tiling
            contourWidth = +args.tileW + radius * 2;
            contourHeight = +args.tileH + radius * 2;
            x = +args.tileX;
            y = +args.tileY;
        } else {
            // dynamic boxes
            contourWidth = +args.boxW + radius * 2;
            contourHeight = +args.boxH + radius * 2;
            x = +args.boxX;
            y = +args.boxY;
        }

        var translatedData = data.map(d => ({
            x: d.cx - (x - radius),
            y: d.cy - (y - radius),
            w: +JSON.parse(d.clusterAgg)["count(*)"]
        }));
        contours = d3
            .contourDensity()
            .x(d => d.x)
            .y(d => d.y)
            .weight(d => d.w)
            .size([contourWidth, contourHeight])
            .cellSize(cellSize)
            .bandwidth(bandwidth)
            .thresholds(function(v) {
                // var step = 0.05 / Math.pow(decayRate, +args.pyramidLevel) * 6;
                // var stop = d3.max(v);
                var eMax =
                    (0.07 * roughN) /
                    1000 /
                    Math.pow(decayRate, +args.pyramidLevel);
                return d3.range(1e-4, eMax, eMax / 6);
            })(translatedData);

        var color = d3
            .scaleSequential(d3[params.contourColorScheme])
            .domain([
                1e-4,
                (0.04 * roughN) /
                    1000 /
                    Math.pow(decayRate, +args.pyramidLevel) /
                    cellSize /
                    cellSize
            ]);

        svg.selectAll("*").remove();
        var g = svg
            .append("g")
            .attr(
                "transform",
                "translate(" + (x - radius) + " " + (y - radius) + ")"
            );

        g.attr("fill", "none")
            .attr("stroke", "black")
            .attr("stroke-opacity", 0)
            .attr("stroke-linejoin", "round")
            .selectAll("path")
            .data(contours)
            .enter()
            .append("path")
            .attr("d", d3.geoPath())
            .style("fill", d => color(d.value))
            .style("opacity", params.contourOpacity);

        ///////////////// uncomment the following for rendering using canvas
        // var canvas = document.createElement("canvas");
        // var ctx = canvas.getContext("2d");
        // (canvas.width = contourWidth), (canvas.height = contourHeight);
        // g.append("foreignObject")
        //     .attr("x", 0)
        //     .attr("y", 0)
        //     .attr("width", contourWidth)
        //     .attr("height", contourHeight)
        //     .style("overflow", "auto")
        //     .node()
        //     .appendChild(canvas);
        // d3.select(canvas).style("opacity", REPLACE_ME_CONTOUR_OPACITY);
        // var path = d3.geoPath().context(ctx);
        // for (var i = 0; i < contours.length; i++) {
        //     var contour = contours[i];
        //     var threshold = contour.value;
        //     ctx.beginPath(),
        //         (ctx.fillStyle = color(threshold)),
        //         path(contour),
        //         ctx.fill();
        // }
    }

    function renderHeatmapBody() {
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        var agg;
        var curMeasure = params.aggMeasures[0];
        agg = curMeasure.function + "(" + curMeasure.field + ")";
        var radius = params.heatmapRadius;
        var heatmapWidth, heatmapHeight, x, y;
        if ("tileX" in args) {
            // tiling
            heatmapWidth = +args.tileW + radius * 2;
            heatmapHeight = +args.tileH + radius * 2;
            x = +args.tileX;
            y = +args.tileY;
        } else {
            // dynamic boxes
            heatmapWidth = +args.boxW + radius * 2;
            heatmapHeight = +args.boxH + radius * 2;
            x = +args.boxX;
            y = +args.boxY;
        }

        var translatedData = data.map(d => ({
            x: d.cx - (x - radius),
            y: d.cy - (y - radius),
            w: +JSON.parse(d.clusterAgg)[agg]
        }));

        // render heatmap
        svg.selectAll("*").remove();
        var g = svg
            .append("g")
            .attr(
                "transform",
                "translate(" + (x - radius) + " " + (y - radius) + ")"
            );

        // from heatmap.js
        // https://github.com/pa7/heatmap.js/blob/4e64f5ae5754c84fea363f0fcf24bea4795405ff/src/renderer/canvas2d.js#L23
        var _getPointTemplate = function(radius) {
            var tplCanvas = document.createElement("canvas");
            var tplCtx = tplCanvas.getContext("2d");
            var x = radius;
            var y = radius;
            tplCanvas.width = tplCanvas.height = radius * 2;

            var gradient = tplCtx.createRadialGradient(x, y, 5, x, y, radius);
            gradient.addColorStop(0, "rgba(0,0,0,1)");
            gradient.addColorStop(1, "rgba(0,0,0,0)");
            tplCtx.fillStyle = gradient;
            tplCtx.fillRect(0, 0, 2 * radius, 2 * radius);
            return tplCanvas;
        };

        // draw all data points in black circles
        var alphaCanvas = document.createElement("canvas");
        alphaCanvas.width = heatmapWidth;
        alphaCanvas.height = heatmapHeight;
        var minWeight = params[args.ssvId + "_" + agg + "_min"]; // set in the BGRP (back-end generated rendering params)
        var maxWeight = params[args.ssvId + "_" + agg + "_max"]; // set in the BGRP
        var alphaCtx = alphaCanvas.getContext("2d");
        var tpl = _getPointTemplate(radius);
        for (var i = 0; i < translatedData.length; i++) {
            var tplAlpha =
                (translatedData[i].w - minWeight) / (maxWeight - minWeight);
            alphaCtx.globalAlpha = tplAlpha < 0.01 ? 0.01 : tplAlpha;
            alphaCtx.drawImage(
                tpl,
                translatedData[i].x - radius,
                translatedData[i].y - radius
            );
        }

        // colorize the black circles using GPU.js
        var imageData = alphaCtx.getImageData(
            0,
            0,
            heatmapWidth,
            heatmapHeight
        );
        const canvas = document.createElement("canvas");
        canvas.width = heatmapWidth;
        canvas.height = heatmapHeight;
        const gl = canvas.getContext("webgl2", {premultipliedAlpha: false});
        var gpu = new GPU({canvas, webGl: gl});
        const render = gpu
            .createKernel(function(imageData) {
                const alpha =
                    imageData[
                        ((this.constants.height - this.thread.y) *
                            this.constants.width +
                            this.thread.x) *
                            4 +
                            3
                    ];
                const rgb = getColor(alpha / 255.0);
                this.color(
                    rgb[0] / 255.0,
                    rgb[1] / 255.0,
                    rgb[2] / 255.0,
                    alpha / 255.0
                );
            })
            .setOutput([heatmapWidth, heatmapHeight])
            .setGraphical(true)
            .setFunctions([
                function getColor(t) {
                    // equivalent d3 color scale:
                    // d3.scaleLinear()
                    // .domain([0, 0.25, 0.55, 0.85, 1])
                    // .range(["rgb(255,255,255)", "rgb(0,0,255)",
                    // "rgb(0,255,0)", "rgb(255, 255, 0)", "rgb(255,0,0)"]);
                    // hardcode here because we can't access d3 in GPU.js's kernel function
                    if (t >= 0 && t <= 0.25)
                        return [
                            255 + ((0 - 255) * t) / 0.25,
                            255 + ((0 - 255) * t) / 0.25,
                            255
                        ];
                    if (t >= 0.25 && t <= 0.55)
                        return [
                            0,
                            (255 * (t - 0.25)) / 0.3,
                            255 + ((0 - 255) * (t - 0.25)) / 0.3
                        ];
                    if (t >= 0.55 && t <= 0.85)
                        return [(255 * (t - 0.55)) / 0.3, 255, 0];
                    if (t >= 0.85 && t <= 1)
                        return [255, 255 + ((0 - 255) * (t - 0.85)) / 0.15, 0];
                    return [255, 255, 255];
                }
            ])
            .setConstants({width: heatmapWidth, height: heatmapHeight});
        render(imageData.data);

        g.append("foreignObject")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", heatmapWidth)
            .attr("height", heatmapHeight)
            .style("overflow", "auto")
            .node()
            .appendChild(render.canvas);
        d3.select(render.canvas).style("opacity", params.heatmapOpacity);
    }

    function renderRadarBody() {
        if (!data || data.length == 0) return;
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        var g = svg.append("g");
        g.style("opacity", 0);

        // Step 1: Pre-process clusterAgg
        params.processClusterAgg(data, params);

        // Step 2: append radars
        var radars = g
            .selectAll("g.radar")
            .data(data)
            .enter();

        // radar chart, for average
        var radius = params.radarRadius;

        // ticks
        var ticks = [];
        for (var i = 0; i < params.radarTicks; i++)
            ticks.push((i + 1) * (radius / params.radarTicks));

        // line
        var line = d3
            .line()
            .x(d => d.x)
            .y(d => d.y);

        function getPathCoordinates(d) {
            var coordinates = [];
            for (var i = 0; i < params.aggMeasures.length; i++) {
                var curMeasure = params.aggMeasures[i];
                if (!("extent" in curMeasure)) continue;
                var curAggKey =
                    curMeasure.function + "(" + curMeasure.field + ")";
                var angle =
                    Math.PI / 2 + (2 * Math.PI * i) / params.aggMeasures.length;
                // average
                coordinates.push(
                    angleToCoordinate(
                        d,
                        angle,
                        curMeasure.extent[0],
                        curMeasure.extent[1],
                        +d.clusterAgg[curAggKey]
                    )
                );
            }
            coordinates.push(coordinates[0]);
            return coordinates;
        }

        function angleToCoordinate(d, angle, lo, hi, value) {
            var curScale = d3
                .scaleLinear()
                .domain([lo, hi])
                .range([0, radius]);
            var x = Math.cos(angle) * curScale(value);
            var y = Math.sin(angle) * curScale(value);
            return {x: +d.cx + x, y: +d.cy - y};
        }

        radars.each((p, j, nodes) => {
            // ticks
            for (var i = ticks.length - 1; i >= 0; i--) {
                d3.select(nodes[j])
                    .append("circle")
                    .attr("cx", d => d.cx)
                    .attr("cy", d => d.cy)
                    .attr("fill", "none")
                    .attr("stroke", "gray")
                    .attr("r", ticks[i])
                    .classed("kyrix-retainsizezoom", true);
            }
            // axis & labels
            for (var i = 0; i < params.aggMeasures.length; i++) {
                var curMeasure = params.aggMeasures[i];
                if (!("extent" in curMeasure)) continue;
                var angle =
                    Math.PI / 2 + (2 * Math.PI * i) / params.aggMeasures.length;
                var lineCoords = angleToCoordinate(
                    p,
                    angle,
                    curMeasure.extent[0],
                    curMeasure.extent[1],
                    curMeasure.extent[1]
                );
                var labelCoords = angleToCoordinate(
                    p,
                    angle,
                    curMeasure.extent[0],
                    curMeasure.extent[1],
                    curMeasure.extent[1] * 1.1
                );

                //draw axis line
                d3.select(nodes[j])
                    .append("line")
                    .attr("x1", p.cx)
                    .attr("y1", p.cy)
                    .attr("x2", lineCoords.x)
                    .attr("y2", lineCoords.y)
                    .classed("kyrix-retainsizezoom", true)
                    .attr("stroke", "black");

                //draw axis label
                d3.select(nodes[j])
                    .append("text")
                    .classed("label", true)
                    .attr("x", labelCoords.x)
                    .attr("y", labelCoords.y)
                    .classed("kyrix-retainsizezoom", true)
                    .text(curMeasure.field.substr(0, 3).toUpperCase());
            }
            // path
            var coordinates = getPathCoordinates(p);
            d3.select(nodes[j])
                .append("path")
                .datum(coordinates)
                .attr("d", line)
                .classed("radar", true)
                .attr("stroke-width", 3)
                .attr("stroke", "darkorange")
                .attr("fill", "darkorange")
                .attr("stroke-opacity", 0.8)
                .attr("fill-opacity", 0.5)
                .classed("kyrix-retainsizezoom", true)
                .datum(p);

            d3.select(nodes[j])
                .append("text")
                .text(function(d) {
                    return d3.format(
                        params.numberFormat
                    )(d.clusterAgg["count(*)"]);
                })
                .attr("font-size", 25)
                .attr("x", function(d) {
                    return d.cx;
                })
                .attr("y", function(d) {
                    return d.cy;
                })
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .style("fill-opacity", 1)
                .style("fill", "navy")
                .style("pointer-events", "none")
                .classed("kyrix-retainsizezoom", true);
        });

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        g.selectAll(".radarhover")
            .data(data)
            .enter()
            .append("circle")
            .classed("radarhover", true)
            .attr("cx", d => d.cx)
            .attr("cy", d => d.cy)
            .attr("r", radius)
            .style("opacity", 0);
        var hoverSelector = ".radarhover";
    }

    function renderPieBody() {
        if (!data || data.length == 0) return;
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        var aggKeyDelimiter = params.aggKeyDelimiter;
        var parse = params.parsePathIntoSegments;
        var translate = params.translatePathSegments;
        var serialize = params.serializePath;

        var g = svg.append("g");
        g.style("opacity", 0);

        // Step 1: Pre-process clusterAgg
        params.processClusterAgg(data, params);

        // Step 2: append pies
        var pie = d3.pie().value(function(d) {
            return d.value;
        });

        var aggKeys = [];
        for (var i = 0; i < params.aggDomain.length; i++)
            aggKeys.push(
                params.aggDomain[i] +
                    (params.aggDomain[i] == "" ? "" : aggKeyDelimiter) +
                    params.aggMeasures[0].function +
                    "(" +
                    params.aggMeasures[0].field +
                    ")"
            );
        var color = d3.scaleOrdinal(d3.schemeTableau10).domain(aggKeys);
        var arc = d3
            .arc()
            .innerRadius(params.pieInnerRadius)
            .outerRadius(params.pieOuterRadius)
            .cornerRadius(params.pieCornerRadius)
            .padAngle(params.padAngle);
        var scalePercent = d3
            .scaleLinear()
            .domain([0, 2 * Math.PI])
            .range([0, 1]);
        var formatter = d3.format(".1%");
        var slicedata = [];

        data.forEach((p, j) => {
            p.arcs = pie(
                d3
                    .entries(p.clusterAgg)
                    .filter(d => aggKeys.indexOf(d.key) >= 0)
            );
            var cooked = p.arcs.map(entry => {
                // for (var index in pos) entry[pos[index]] = +p[pos[index]];
                for (var key in p) entry[key] = p[key];
                entry.data.percentage = formatter(
                    scalePercent(entry.endAngle - entry.startAngle)
                );
                entry.convexHull = p.convexHull;
                return entry;
            });
            slicedata = slicedata.concat(cooked);
        });

        // slices
        g.selectAll("path.slice")
            .data(slicedata)
            .enter()
            .append("path")
            .attr("class", function(d, i) {
                return `value ${d.data.key} kyrix-retainsizezoom`;
            })
            .attr("d", (d, i, nodes) => {
                return serialize(translate(parse(arc(d)), d.cx, d.cy));
            })
            .attr("fill", function(d, i) {
                var ret = color(d.data.key);
                return ret;
            });

        // numbers
        g.selectAll("text.cluster_num")
            .data(data)
            .enter()
            .append("text")
            .classed("cluster_num", true)
            .text(d =>
                d3.format(params.numberFormat)(+d.clusterAgg["count(*)"])
            )
            .attr("x", d => +d.cx)
            .attr("y", d => +d.cy - params.pieOuterRadius)
            // .attr("dy", ".35em")
            .attr("font-size", params.pieOuterRadius / 2.5)
            .attr("text-anchor", "middle")
            .style("fill-opacity", 0.8)
            .style("fill", "grey")
            .style("pointer-events", "none")
            .classed("kyrix-retainsizezoom", true);

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        g.selectAll(".piehover")
            .data(data)
            .enter()
            .append("circle")
            .classed("piehover", true)
            .attr("cx", d => d.cx)
            .attr("cy", d => d.cy)
            .attr("r", params.pieOuterRadius)
            .style("opacity", 0);
        var hoverSelector = ".piehover";
    }

    function renderDotBody() {
        if (!data || data.length == 0) return;

        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        var g = svg.append("g");
        params.processClusterAgg(data, params);

        // size scale
        var dotSizeScale = null;
        if ("dotSizeColumn" in params)
            dotSizeScale = d3
                .scaleLinear()
                .domain(params.dotSizeDomain)
                .range([0, params.dotMaxSize]);

        // color scale
        var dotColorScale = null;
        if ("dotColorColumn" in params)
            dotColorScale = d3.scaleOrdinal(
                params.dotColorDomain,
                d3.schemeTableau10
            );

        g.selectAll(".ssvdot")
            .data(data)
            .join("circle")
            .attr("r", d =>
                "dotSizeColumn" in params
                    ? dotSizeScale(+d[params.dotSizeColumn])
                    : params.dotMaxSize
            )
            .attr("cx", d => +d.cx)
            .attr("cy", d => +d.cy)
            .style("fill-opacity", 0)
            .attr("stroke", d =>
                "dotColorColumn" in params
                    ? dotColorScale(d[params.dotColorColumn])
                    : "#38c2e0"
            )
            .style("stroke-width", "2px")
            .classed("kyrix-retainsizezoom", true);
    }

    function regularHoverBody() {
        function convexRenderer(svg, d) {
            var line = d3
                .line()
                .x(d => d.x)
                .y(d => d.y);
            var g = svg.append("g");
            g.append("path")
                .datum(d)
                .attr("class", "convexHull")
                .attr("id", "ssv_boundary_hover")
                .attr("d", d => line(d.convexHull))
                .style("fill-opacity", 0)
                .style("stroke-width", 3)
                .style("stroke-opacity", 0.5)
                .style("stroke", "grey")
                .style("pointer-events", "none");
        }

        function bboxRenderer(svg, d) {
            var minx = 1e100,
                miny = 1e100;
            var maxx = -1e100,
                maxy = -1e100;
            for (var i = 0; i < d.convexHull.length; i++) {
                minx = Math.min(minx, d.convexHull[i].x);
                miny = Math.min(miny, d.convexHull[i].y);
                maxx = Math.max(maxx, d.convexHull[i].x);
                maxy = Math.max(maxy, d.convexHull[i].y);
            }
            g = svg.append("g");
            g.append("rect")
                .attr("x", minx)
                .attr("y", miny)
                .attr("rx", 5)
                .attr("ry", 5)
                .attr("width", maxx - minx)
                .attr("height", maxy - miny)
                .style("fill-opacity", 0)
                .style("stroke-width", 3)
                .style("stroke-opacity", 0.5)
                .style("stroke", "grey")
                .style("pointer-events", "none");
        }

        function tabularRankListRenderer(svg, data, args) {
            var rpKey =
                "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
            var params = args.renderingParams[rpKey];
            var charW = 8;
            var charH = 15;
            var paddingH = 10;
            var paddingW = 14;
            var headerH = charH + 20;

            var g = svg
                .append("g")
                .attr("id", "tabular_hover")
                .attr("class", "tabular ranklist");
            var fields = params.hoverTableFields;
            var widths = [];
            var totalW = 0,
                totalH = data.length * (charH + paddingH) + headerH;
            for (var i = 0; i < fields.length; i++) {
                var maxlen = 0;
                for (var j = 0; j < data.length; j++) {
                    if (!isNaN(data[j][fields[i]]))
                        data[j][fields[i]] = d3.format(params.numberFormat)(
                            +data[j][fields[i]]
                        );
                    maxlen = Math.max(
                        maxlen,
                        data[j][fields[i]].toString().length
                    );
                }
                maxlen = Math.max(maxlen, fields[i].length);
                widths.push(maxlen * charW + paddingW);
                totalW += widths[i];
            }
            var basex = data[0].cx - totalW / 2;
            var basey = data[0].cy - totalH / 2;
            var runx = basex,
                runy = basey;
            for (var i = 0; i < fields.length; i++) {
                var width = widths[i];
                // th
                g.append("rect")
                    .attr("x", runx)
                    .attr("y", runy)
                    .attr("width", width)
                    .attr("height", headerH)
                    .attr("style", "fill: #888888; stroke: #c0c4c3;");
                g.append("text")
                    .text(fields[i])
                    .attr("x", runx + width / 2)
                    .attr("y", runy + headerH / 2)
                    .attr("style", "fill: #f8f4ed;")
                    .style("text-anchor", "middle")
                    .style("font-size", charH + "px")
                    .attr("dy", "0.35em");
                runy += headerH;
                // tr
                for (var j = 0; j < data.length; j++) {
                    g.append("rect")
                        .attr("x", runx)
                        .attr("y", runy)
                        .attr("width", width)
                        .attr("height", charH + paddingH)
                        .attr("style", "fill: #ebebeb; stroke: #c0c4c3;");
                    g.append("text")
                        .text(data[j][fields[i]])
                        .attr("x", runx + width / 2)
                        .attr("y", runy + (charH + paddingH) / 2)
                        .style("text-anchor", "middle")
                        .style("font-size", charH + "px")
                        .attr("dy", "0.35em");
                    runy += charH + paddingH;
                }
                runx += width;
                runy = basey;
            }
        }

        // ranklist
        if ("hoverRankListMode" in params) {
            var rankListRenderer;
            if (params.hoverRankListMode == "tabular")
                rankListRenderer = tabularRankListRenderer;
            else rankListRenderer = params.hoverCustomRenderer;
            g.selectAll(hoverSelector)
                .on("mouseenter.ranklist", function(d) {
                    // deal with top-k here
                    // run rankListRenderer for each of the top-k
                    // for tabular renderer, add a header first
                    // use params.hoverRankListOrientation for deciding layout
                    // use params.bboxH(W) for bounding box size
                    var g = svg.append("g").attr("id", "ssv_ranklist_hover");
                    var topKData = d.clusterAgg.topk;
                    var topk = topKData.length;
                    for (var i = 0; i < topk; i++) {
                        topKData[i].cx = +d.cx;
                        topKData[i].cy = +d.cy;
                    }
                    if (params.hoverRankListMode == "tabular")
                        rankListRenderer(g, topKData, args);
                    else {
                        var orientation = params.hoverRankListOrientation;
                        var bboxW = params.bboxW;
                        var bboxH = params.bboxH;
                        for (var i = 0; i < topk; i++) {
                            var transX = 0,
                                transY = 0;
                            if (orientation == "vertical")
                                transY = bboxH * (-topk / 2.0 + 0.5 + i);
                            else transX = bboxW * (-topk / 2.0 + 0.5 + i);
                            topKData[i].cx += transX;
                            topKData[i].cy += transY;
                            rankListRenderer(g, [topKData[i]], args);
                        }
                    }
                    g.style("opacity", 0.8)
                        .style("pointer-events", "none")
                        .selectAll("g")
                        .selectAll("*")
                        .datum({cx: +d.cx, cy: +d.cy})
                        .classed("kyrix-retainsizezoom", true)
                        .each(function() {
                            zoomRescale(args.viewId, this);
                        });
                })
                .on("mouseleave.ranklist", function() {
                    d3.selectAll("#ssv_ranklist_hover").remove();
                });
        }

        // boundary
        if ("hoverBoundary" in params)
            g.selectAll(hoverSelector)
                .on("mouseover.boundary", function(d) {
                    var g = svg.append("g").attr("id", "ssv_boundary_hover");
                    if (params.hoverBoundary == "convexhull")
                        convexRenderer(g, d);
                    else if (params.hoverBoundary == "bbox") bboxRenderer(g, d);
                })
                .on("mouseleave.boundary", function() {
                    d3.selectAll("#ssv_boundary_hover").remove();
                });
    }

    function customClusterModeHoverBody() {
        var rpKey = "ssv_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        params.processClusterAgg(data, params);
    }

    function KDEObjectHoverBody() {
        // no topk for KDE for now
        var objectRenderer = params.hoverCustomRenderer;
        if (objectRenderer == null) return;
        var hiddenRectSize = 100;
        svg.append("g")
            .selectAll("rect")
            .data(data)
            .enter()
            .append("rect")
            .attr("x", d => d.cx - hiddenRectSize / 2)
            .attr("y", d => d.cy - hiddenRectSize / 2)
            .attr("width", hiddenRectSize)
            .attr("height", hiddenRectSize)
            .attr("fill-opacity", 0)
            .on("mouseover", function(d) {
                var svgNode;
                if ("tileX" in args) svgNode = d3.select(svg.node().parentNode);
                else svgNode = svg;
                objectRenderer(svgNode, [d], args);
                var lastG = svgNode.node().childNodes[
                    svgNode.node().childElementCount - 1
                ];
                d3.select(lastG)
                    .attr("id", "ssv_tooltip")
                    .style("opacity", 0.8)
                    .style("pointer-events", "none")
                    .selectAll("*")
                    .classed("kyrix-retainsizezoom", true)
                    .each(function() {
                        zoomRescale(args.viewId, this);
                    });
            })
            .on("mouseleave", function() {
                d3.select("#ssv_tooltip").remove();
            });
    }

    var renderFuncBody;
    if (this.clusterMode == "custom") {
        renderFuncBody =
            "(" +
            this.clusterCustomRenderer.toString() +
            ")(svg, data, args);\n";
        if (this.clusterParams.clusterCount)
            renderFuncBody += getBodyStringOfFunction(
                renderObjectClusterNumBody
            );
        if (this.hoverSelector) {
            renderFuncBody +=
                'var hoverSelector = "' + this.hoverSelector + '";\n';
            renderFuncBody += getBodyStringOfFunction(
                customClusterModeHoverBody
            );
            renderFuncBody += getBodyStringOfFunction(regularHoverBody);
        }
    } else if (this.clusterMode == "circle") {
        // render circle
        renderFuncBody = getBodyStringOfFunction(renderCircleBody);
        renderFuncBody += getBodyStringOfFunction(regularHoverBody);
    } else if (this.clusterMode == "contour") {
        renderFuncBody = getBodyStringOfFunction(renderContourBody);
        renderFuncBody += getBodyStringOfFunction(KDEObjectHoverBody);
    } else if (this.clusterMode == "heatmap") {
        renderFuncBody = getBodyStringOfFunction(renderHeatmapBody);
        renderFuncBody += getBodyStringOfFunction(KDEObjectHoverBody);
    } else if (this.clusterMode == "radar") {
        renderFuncBody = getBodyStringOfFunction(renderRadarBody);
        renderFuncBody += getBodyStringOfFunction(regularHoverBody);
    } else if (this.clusterMode == "pie") {
        renderFuncBody = getBodyStringOfFunction(renderPieBody);
        renderFuncBody += getBodyStringOfFunction(regularHoverBody);
    } else if (this.clusterMode == "dot") {
        renderFuncBody = getBodyStringOfFunction(renderDotBody);
        renderFuncBody += getBodyStringOfFunction(regularHoverBody);
    }
    return new Function("svg", "data", "args", renderFuncBody);
}

//define prototype
Graph.prototype = {
    getLayerRenderer
};

// exports
module.exports = {
    Graph
};