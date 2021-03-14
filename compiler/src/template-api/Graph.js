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

//define prototype
Graph.prototype = {
};

// exports
module.exports = {
    Graph,
    processClusterAgg
};