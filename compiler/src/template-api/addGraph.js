const Canvas = require("../Canvas").Canvas;
const View = require("../View").View;
const Jump = require("../Jump").Jump;
const Layer = require("../Layer").Layer;
const Transform = require("../Transform").Transform;

/**
 * Add the graph object to a project, this will create a hierarchy of canvases that form a pyramid shape
 * @param graph: a Graph object
 * @param args: a dictionary that contains customization parameters, see doc
 */
function addGraph(graph, args) {
    if (args == null) args = {};

    // add to project
    this.graphs.push(graph);

    // add stuff to renderingParam
    var renderingParams = {
        textwrap: require("./Utilities").textwrap,
        processClusterAggNodes: require("./Graph").processClusterAggNodes,
        processClusterAggEdges: require("./Graph").processClusterAggEdges,
        serializePath: require("./Utilities").serializePath,
        translatePathSegments: require("./Utilities").translatePathSegments,
        parsePathIntoSegments: require("./Utilities").parsePathIntoSegments,
        // aggKeyDelimiter: ssv.aggKeyDelimiter,
        zoomFactor: graph.zoomFactor,
        fadeInDuration: 200
    };
    renderingParams = {
        ...renderingParams,
        ...graph.layoutParams,
        ...graph.clusterParams,
        ...graph.hoverParams
    };
    var rpKey = "graph_" + (this.graphs.length - 1);
    var rpDict = {};
    rpDict[rpKey] = renderingParams;
    this.addRenderingParams(rpDict);

    // console.log("----- Adding graph object to project-------");
    // construct canvases
    var curPyramid = [];
    // dummy transforms
    var transformNodes = new Transform(graph.queryNodes, graph.db, "", [], true);
    var transformEdges = new Transform(graph.queryEdges, graph.db, "", [], true);
    var numLevels = graph.numLevels;

    for (var i=0; i<numLevels; i++) {
        var width = (graph.topLevelWidth * Math.pow(graph.zoomFactor, i)) | 0;
        var height = (graph.topLevelHeight * Math.pow(graph.zoomFactor, i)) | 0;

        // construct a new canvas
        var curCanvas;
        if (args.pyramid) {
            curCanvas = args.pyramid[i];
            if (Math.abs(curCanvas.width - width) > 1e-3 || Math.abs(curCanvas.height - height) > 1e-3)
                throw new Error("Adding Graph: Canvas sizes do not match");
        } else {
            curCanvas = new Canvas(
                "graph" + (this.graphs.length-1) + "_" + "level" + i,
                width,
                height
            );
            this.addCanvas(curCanvas);
        }
        curPyramid.push(curCanvas);

        // create node and edge layers
        var curNodeLayer = new Layer(transformNodes, false);
        var curEdgeLayer = new Layer(transformEdges, false);
        curCanvas.addLayer(curNodeLayer);
        curCanvas.addLayer(curEdgeLayer);

        // set fetching scheme
        curNodeLayer.setFetchingScheme("dbox", true);
        curEdgeLayer.setFetchingScheme("dbox", true);
        //curLayer.setFetchingScheme("tiling");

        // set ssv ID
        curNodeLayer.setIndexerType("GraphInMemoryIndexer");
        //curLayer.setIndexerType("SSVCitusIndexer");
        curNodeLayer.setGraphId(this.graphs.length - 1 + "_node_" + i);
        curEdgeLayer.setIndexerType("GraphInMemoryIndexer");
        //curLayer.setIndexerType("SSVCitusIndexer");
        curEdgeLayer.setGraphId(this.graphs.length - 1 + "_edge_" + i);

        // dummy placement
        curNodeLayer.addPlacement({
            centroid_x: "con:0",
            centroid_y: "con:0",
            width: "con:0",
            height: "con:0"
        });
        curEdgeLayer.addPlacement({
            centroid_x: "con:0",
            centroid_y: "con:0",
            width: "con:0",
            height: "con:0"
        });

        // construct rendering function
        curNodeLayer.addRenderingFunc(graph.getNodeLayerRenderer());
        curEdgeLayer.addRenderingFunc(graph.getEdgeLayerRenderer());

        // tooltips
        curNodeLayer.addTooltip(graph.tooltipNodeColumns, graph.tooltipNodeAliases);
        curEdgeLayer.addTooltip(graph.tooltipEdgeColumns, graph.tooltipEdgeAliases);
    }

    // literal zooms
    for (var i = 0; i + 1 < graph.numLevels; i++) {
        var hasLiteralZoomIn = false;
        var hasLiteralZoomOut = false;
        for (var j = 0; j < this.jumps.length; j++) {
            if (
                this.jumps[j].sourceId == curPyramid[i].id &&
                this.jumps[j].type == "literal_zoom_in"
            ) {
                if (this.jumps[j].destId != curPyramid[i + 1].id)
                    throw new Error(
                        "Adding Graph: malformed literal zoom pyramid."
                    );
                hasLiteralZoomIn = true;
            }
            if (
                this.jumps[j].sourceId == curPyramid[i + 1].id &&
                this.jumps[j].type == "literal_zoom_out"
            ) {
                if (this.jumps[j].destId != curPyramid[i].id)
                    throw new Error(
                        "Adding Graph: malformed literal zoom pyramid."
                    );
                hasLiteralZoomOut = true;
            }
        }
        if (!hasLiteralZoomIn)
            this.addJump(new Jump(curPyramid[i], curPyramid[i + 1], "literal_zoom_in"));
        if (!hasLiteralZoomOut)
            this.addJump(new Jump(curPyramid[i + 1], curPyramid[i], "literal_zoom_out"));
    }

    // create a new view if not specified
    if (!args.view) {
        var viewId = "graph" + (this.graphs.length - 1);
        var view = new View(viewId, graph.topLevelWidth, graph.topLevelHeight);
        this.addView(view);
        // initialize view
        this.setInitialStates(view, curPyramid[0], 0, 0);
    } else if (!(args.view instanceof View))
        throw new Error("Adding Graph: view must be a View object");

    return {pyramid: curPyramid, view: args.view ? args.view : view};
}

module.exports = {
    addGraph
};