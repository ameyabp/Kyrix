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

    // console.log("-------- Successfully verified schema ---------")
    /*******************************************************************************
     * check constraints/add defaults that can't be easily expressed by json-schema
     *******************************************************************************/    
    // succinct object notation of the measures
    if (!("length" in args.marks.cluster.aggregate.measures)) {
        var measureArray = [];
        for (
            var i = 0;
            i < args.marks.cluster.aggregate.measures.fields.length;
            i++
        )
            measureArray.push({
                field: args.marks.cluster.aggregate.measures.fields[i],
                function: args.marks.cluster.aggregate.measures.function
            });
        args.marks.cluster.aggregate.measures = measureArray;
    }
    
    if ("rankList" in args.marks.hover) {
        if ("tooltip" in args.marks.hover)
            throw new Error(
                "Constructing Graph: rankList and tooltip cannot be specified together."
            );
    }

    if ("tooltip" in args.marks.hover) {
        if (
            "aliases" in args.marks.hover.tooltip &&
            args.marks.hover.tooltip.aliases.length !==
                args.marks.hover.tooltip.columns.length
        )
            throw new Error(
                "Constructing Graph: tooltip aliases (marks.hover.tooltip.aliases) " +
                    "must have the same number of elements as columns (marks.hover.tooltip.columns)."
            );
    }

    this.db = args.data.db;
    this.queryNodes = args.data.queryNodes;
    this.queryEdges = args.data.queryEdges;

    this.numLevels = args.marks.cluster.numClusters.length;
    this.topLevelWidth = args.config.topLevelWidth;
    this.topLevelHeight = args.config.topLevelHeight;
    this.zoomFactor = args.config.zoomFactor;

    /************************
     * setting cluster params
     ************************/
    this.clusterParams = {};
    this.clusterParams.numClusters = args.marks.cluster.numClusters;
    this.clusterParams.clusteringAlgorithm = args.marks.cluster.algorithm;
    this.clusterParams.clusteringRandomStateParameter = args.marks.cluster.randomState;
    this.clusterParams.aggregateParams = {
        aggMeasures: args.marks.cluster.aggregate.measures,
        aggDimensions: args.marks.cluster.aggregate.dimensions
    };

    /************************
     * setting hover params
     ************************/
    this.hoverParams = {};
    if ("rankList" in args.marks.hover) {
        // get in everything in config
        this.hoverParams = args.marks.hover.rankList.config;

        // mode: currently either tabular or custom
        this.hoverParams.hoverRankListMode = args.marks.hover.rankList.mode;

        // table fields
        if (args.marks.hover.rankList.mode == "tabular")
            this.hoverParams.hoverTableFields = args.marks.hover.rankList.fields;

        // custom topk renderer
        if (args.marks.hover.rankList.mode == "custom")
            this.hoverParams.hoverCustomRenderer = args.marks.hover.rankList.custom;

        // topk is 1 by default if unspecified
        this.hoverParams.topk = args.marks.hover.rankList.topk;

        // orientation of custom ranks
        this.hoverParams.hoverRankListOrientation = args.marks.hover.rankList.orientation;
    }
    if ("boundary" in args.marks.hover)
        this.hoverParams.hoverBoundary = args.marks.hover.boundary;
    this.topk = "topk" in this.hoverParams ? this.hoverParams.topk : 0;
    this.hoverSelector =
        "selector" in args.marks.hover ? args.marks.hover.selector : null;
    this.tooltipColumns = this.tooltipAliases = null;
    if ("tooltip" in args.marks.hover) {
        this.tooltipColumns = args.marks.hover.tooltip.columns;
        if ("aliases" in args.marks.hover.tooltip)
            this.tooltipAliases = args.marks.hover.tooltip.aliases;
        else this.tooltipAliases = this.tooltipColumns;
    }
}

// function used for processing cluster aggs
function processClusterAgg(data, params) {

}

// get rendering function for the graph edges layer
function getEdgeLayerRenderer() {
    function renderEdges() {
        var rpKey = "graph_" + args.graphId.substring(0, args.graphId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        params.processClusterAgg(data, params);

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

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        var hoverSelector = "circle";
    }
    return new Function("svg", "data", "args", renderEdges);
}


// get rendering function for the graph nodes layer
function getNodeLayerRenderer() {
    function renderNodes() {
        var rpKey = "graph_" + args.graphId.substring(0, args.graphId.indexOf("_"));
        var params = args.renderingParams[rpKey];
        params.processClusterAgg(data, params);

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
            return max(3, Math.sqrt(d.memberNodeCount));
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

        // fade in
        g.transition()
            .duration(params.fadeInDuration)
            .style("opacity", 1);

        // for hover
        var hoverSelector = "circle";
    }
    return new Function("svg", "data", "args", renderNodes);
}

//define prototype
Graph.prototype = {
    getEdgeLayerRenderer,
    getNodeLayerRenderer
};

// exports
module.exports = {
    Graph,
    processClusterAgg
};