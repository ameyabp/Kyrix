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

    console.log("-------- Successfully verified schema ---------");

    /*******************************************************************************
     * check constraints/add defaults that can't be easily expressed by json-schema
     *******************************************************************************/    
    // succinct object notation of the measures
    if ("cluster" in args.summarization && "aggregate" in args.summarization.cluster) {
        if ("nodes" in args.summarization.cluster.aggregate) {
            if (!("length" in args.summarization.cluster.aggregate.nodes)) {
                var fieldsArray = [];
                var aggFunctionArray = [];
                for (
                    var i = 0;
                    i < args.summarization.cluster.aggregate.nodes.fields.length;
                    i++
                ) {
                    fieldsArray.push(args.summarization.cluster.aggregate.nodes.fields[i]);
                    aggFunctionArray.push(args.summarization.cluster.aggregate.nodes.functions);
                }
                
                args.summarization.cluster.aggregate.nodes.fields = fieldsArray;
                args.summarization.cluster.aggregate.nodes.functions = aggFunctionArray;
            }
            else {
                var fieldsArray = [];
                var aggFunctionArray = [];   
                for (
                    var i = 0;
                    i < args.summarization.cluster.aggregate.nodes.length;
                    i++
                ) {
                    fieldsArray.push(args.summarization.cluster.aggregate.nodes[i].fields);
                    aggFunctionArray.push(args.summarization.cluster.aggregate.nodes[i].functions);
                }
                
                args.summarization.cluster.aggregate.nodes.fields = fieldsArray;
                args.summarization.cluster.aggregate.nodes.functions = aggFunctionArray;
            }
        }
        
        if ("edges" in args.summarization.cluster.aggregate) {
            if (!("length" in args.summarization.cluster.aggregate.edges)) {
                var fieldsArray = [];
                var aggFunctionArray = [];
                for (
                    var i = 0;
                    i < args.summarization.cluster.aggregate.edges.fields.length;
                    i++
                ) {
                    fieldsArray.push(args.summarization.cluster.aggregate.edges.fields[i]);
                    aggFunctionArray.push(args.summarization.cluster.aggregate.edges.functions);
                }
                
                args.summarization.cluster.aggregate.edges.fields = fieldsArray;
                args.summarization.cluster.aggregate.edges.functions = aggFunctionArray;
            }
            else {
                var fieldsArray = [];
                var aggFunctionArray = [];   
                for (
                    var i = 0;
                    i < args.summarization.cluster.aggregate.edges.length;
                    i++
                ) {
                    fieldsArray.push(args.summarization.cluster.aggregate.edges[i].fields);
                    aggFunctionArray.push(args.summarization.cluster.aggregate.edges[i].functions);
                }
                
                args.summarization.cluster.aggregate.edges.fields = fieldsArray;
                args.summarization.cluster.aggregate.edges.functions = aggFunctionArray;
            }
        }
    }

    if ("rankList" in args.marks.hover.nodes) {
        if ("tooltip" in args.marks.hover.nodes)
            throw new Error("Constructing Graph: rankList and tooltip cannot be specified together.");

    }

    if ("rankList" in args.marks.hover.edges) {
        if ("tooltip" in args.marks.hover.edges)
            throw new Error("Constructing Graph: rankList and tooltip cannot be specified together.");

    }

    if ("tooltip" in args.marks.hover.nodes) {
        if ("aliases" in args.marks.hover.nodes.tooltip &&
            (args.marks.hover.nodes.tooltip.aliases.length !== args.marks.hover.nodes.tooltip.columns.length))
            throw new Error(
                "Constructing Graph: tooltip aliases (marks.hover.tooltip.aliases) " +
                    "must have the same number of elements as columns (marks.hover.tooltip.columns)."
            );
    }

    if ("tooltip" in args.marks.hover.edges) {
        if("aliases" in args.marks.hover.edges.tooltip &&
            (args.marks.hover.edges.tooltip.aliases.length !== args.marks.hover.edges.tooltip.columns.length))
            throw new Error(
                "Constructing Graph: tooltip aliases (marks.hover.tooltip.aliases) " +
                    "must have the same number of elements as columns (marks.hover.tooltip.columns)."
            );
    }

    this.nodesCsv = args.data.nodesCsv;
    this.edgesCsv = args.data.edgesCsv;
    this.db = args.data.db;
    this.queryNodes = args.data.queryNodes;
    this.queryEdges = args.data.queryEdges;
    this.directedGraph = args.data.directedGraph;

    this.topLevelWidth = args.config.topLevelWidth;
    this.topLevelHeight = args.config.topLevelHeight;
    this.zoomFactor = args.config.zoomFactor;
    this.projectName = args.config.projectName;

    /************************
     * setting layout params
     ************************/
    this.layoutAlgo = args.layout.name;
    this.layoutParams = [];
    if (args.layout.name == 'openORD') {
        this.layoutParams.push(args.layout.ord_maxLevel);
        this.layoutParams.push(args.layout.ord_startLevel);
        this.layoutParams.push(args.layout.ord_lastCut);
        this.layoutParams.push(args.layout.ord_refineCut);
        this.layoutParams.push(args.layout.ord_finalCut);
    }
    else if (args.layout.name == 'fm3') {
        this.layoutParams.push(args.layout.fm3_param1);
        this.layoutParams.push(args.layout.fm3_param2);
        this.layoutParams.push(args.layout.fm3_param3);
    }
    else {
        // args.layout.name == 'fa2'
        this.layout.algorithm = "fa2";
        this.layoutParams.push(args.layout.fa2_param1);
        this.layoutParams.push(args.layout.fa2_param2);
        this.layoutParams.push(args.layout.fa2_param3);
    }

    /************************
     * setting cluster params
     ************************/
    if ("cluster" in args.summarization) {
        this.clusteringAlgo = args.summarization.cluster.algorithm;
        this.numLevels = args.summarization.cluster.clusterLevels.length+1;
        this.clusterLevels = args.summarization.cluster.clusterLevels;
        this.clusteringParams = [];
        if ("aggregate" in args.summarization.cluster) {
            if ("nodes" in args.summarization.cluster.aggregate) {
                this.clusterAggMeasuresNodesFields = args.summarization.cluster.aggregate.nodes.fields;
                this.clusterAggMeasuresNodesFunctions = args.summarization.cluster.aggregate.nodes.functions;
            }
            if ("edges" in args.summarization.cluster.aggregate) {
                this.clusterAggMeasuresEdgesFields = args.summarization.cluster.aggregate.edges.fields;
                this.clusterAggMeasuresEdgesFunctions = args.summarization.cluster.aggregate.edges.functions;
            }
        }
    }

    /************************
     * setting hover params
     ************************/
    this.hoverParams = {};
    if ("rankList" in args.marks.hover.nodes) {
        this.hoverParams.nodesHover = {}

        // get in everything in config
        this.hoverParams.nodesHover.config = args.marks.hover.nodes.rankList.config;

        // mode: currently either tabular or custom
        this.hoverParams.nodesHover.hoverRankListMode = args.marks.hover.nodes.rankList.mode;

        // table fields
        if (args.marks.hover.nodes.rankList.mode == "tabular")
            this.hoverParams.nodesHover.hoverTableFields = args.marks.hover.nodes.rankList.fields;

        // custom topk renderer
        if (args.marks.hover.nodes.rankList.mode == "custom")
            this.hoverParams.nodesHover.hoverCustomRenderer = args.marks.hover.nodes.rankList.custom;

        // topk is 1 by default if unspecified
        this.hoverParams.nodesHover.topk = args.marks.hover.nodes.rankList.topk;

        // orientation of custom ranks
        this.hoverParams.nodesHover.hoverRankListOrientation = args.marks.hover.nodes.rankList.orientation;

        this.hoverParams.nodesHover.orderBy = args.marks.hover.nodes.rankList.orderBy;
        this.hoverParams.nodesHover.order = args.marks.hover.nodes.rankList.order;
    }
    if ("rankList" in args.marks.hover.edges) {
        this.hoverParams.edgesHover = {}

        // get in everything in config
        this.hoverParams.edgesHover.config = args.marks.hover.edges.rankList.config;

        // mode: currently either tabular or custom
        this.hoverParams.edgesHover.hoverRankListMode = args.marks.hover.edges.rankList.mode;

        // table fields
        if (args.marks.hover.edges.rankList.mode == "tabular")
            this.hoverParams.edgesHover.hoverTableFields = args.marks.hover.edges.rankList.fields;

        // custom topk renderer
        if (args.marks.hover.edges.rankList.mode == "custom")
            this.hoverParams.edgesHover.hoverCustomRenderer = args.marks.hover.edges.rankList.custom;

        // topk is 1 by default if unspecified
        this.hoverParams.edges.topk = args.marks.hover.edges.rankList.topk;

        // orientation of custom ranks
        this.hoverParams.edgesHover.hoverRankListOrientation = args.marks.hover.edges.rankList.orientation;

        this.hoverParams.edgesHover.orderBy = args.marks.hover.edges.rankList.orderBy;
        this.hoverParams.edgesHover.order = args.marks.hover.edges.rankList.order;
    }

    if ("boundary" in args.marks.hover.nodes) {
        this.hoverParams.nodesHoverBoundary = args.marks.hover.nodes.boundary;
    }

    if ("boundary" in args.marks.hover.edges) {
        this.hoverParams.edgesHoverBoundary = args.marks.hover.edges.boundary;
    }

    this.hoverSelector = "selector" in args.marks.hover ? args.marks.hover.selector : null;
    
    this.tooltipNodeColumns = this.tooltipNodeAliases = this.tooltipEdgeColumns = this.tooltipEdgeAliases = null;
    if ("tooltip" in args.marks.hover.nodes) {
        this.tooltipNodeColumns = args.marks.hover.nodes.tooltip.columns;
        if ("aliases" in args.marks.hover.nodes.tooltip)
            this.tooltipNodeAliases = args.marks.hover.nodes.tooltip.aliases;
        else this.tooltipNodeAliases = this.tooltipNodeColumns;
    }

    if ("tooltip" in args.marks.hover.edges) {
        this.tooltipEdgeColumns = args.marks.hover.edges.tooltip.columns;
        if ("aliases" in args.marks.hover.edges.tooltip)
            this.tooltipEdgeAliases = args.marks.hover.edges.tooltip.aliases;
        else this.tooltipEdgeAliases = this.tooltipEdgeColumns;
    }
}

// function used for processing cluster aggs
function processClusterAggEdges(data, params) {

}

// get rendering function for the graph edges layer
function getEdgeLayerRenderer() {
    function renderEdges() {
        var rpKey = "graph_" + args.graphId.substring(0, args.graphId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        // params.processClusterAggEdges(data, params);

        g = svg.append("g").attr("id", "linkLayer");
        g.selectAll("line")
        .data(data)
        .enter()
        .append("line")
        .attr("x1", function(d) {
            return d.n1x;
        })
        .attr("y1", function(d) {
            return d.n1y;
        })
        .attr("x2", function(d) {
            return d.n2x;
        })
        .attr("y2", function(d) {
            return d.n2y;
        })
        .attr("stroke-width", function(d) {
            return Math.max(3, Math.sqrt(parseFloat(d._memberedgecount)));
        })
        .style("stroke", "rgba(225, 225, 225, 0.5)")
        .on("mouseover", function(d) {
            d3.select(this).style("stroke", "rgba(0, 0, 0, 0.8)");
        })
        .on("mouseout", function(d) {
            d3.select(this).style("stroke", "rgba(225, 225, 225, 0.5)");
        });

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        var hoverSelector = "line";
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
                "graph_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
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
            console.log("rohila found rankListMode for hover with selector " + hoverSelector);
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

    var renderFuncBody = getBodyStringOfFunction(renderEdges);
    renderFuncBody += getBodyStringOfFunction(regularHoverBody);

    return new Function("svg", "data", "args", renderFuncBody);
}

// function used for processing cluster aggs
function processClusterAggNodes(data, params) {

}

// get rendering function for the graph nodes layer
function getNodeLayerRenderer() {
    function renderNodes() {
        var rpKey = "graph_" + args.graphId.substring(0, args.graphId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        // params.processClusterAggNodes(data, params);

        g = svg.append("g").attr("id", "nodeLayer");
        g.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
            return d.cx;
        })
        .attr("cy", function(d) {
            return d.cy;
        })
        .attr("r", function(d) {
            return Math.max(10, Math.sqrt(parseFloat(d._membernodecount)));
        })
        .attr("fill", function(d) {
            return "rgba(255, 0, 0, 0.7)";
        })
        .on("mouseover", function(d) {
            d3.select("#linkLayer").selectAll("line")
                .filter(function(l) {
                    return l._id.includes(d._id);
                })
                .style("stroke", "rgba(0, 0, 0, 0.8)");
        })
        .on("mouseout", function(d) {
            d3.select("#linkLayer").selectAll("line")
                .filter(function(l) {
                    return l._id.includes(d._id);
                })
                .style("stroke", "rgba(225, 225, 225, 0.5)");
        });

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        var hoverSelector = "circle";
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
                "graph_" + args.ssvId.substring(0, args.ssvId.indexOf("_"));
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
            console.log("rohila found rankListMode for hover with selector " + hoverSelector);
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

    var renderFuncBody = getBodyStringOfFunction(renderNodes);
    renderFuncBody += getBodyStringOfFunction(regularHoverBody);

    return new Function("svg", "data", "args", renderFuncBody);
}

//define prototype
Graph.prototype = {
    getEdgeLayerRenderer,
    getNodeLayerRenderer
};

// exports
module.exports = {
    Graph,
    processClusterAggNodes,
    processClusterAggEdges,
};