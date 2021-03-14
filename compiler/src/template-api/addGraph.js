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
        processClusterAgg: require("./Graph").processClusterAgg,
        serializePath: require("./Utilities").serializePath,
        translatePathSegments: require("./Utilities").translatePathSegments,
        parsePathIntoSegments: require("./Utilities").parsePathIntoSegments,
        // aggKeyDelimiter: ssv.aggKeyDelimiter,
        zoomFactor: graph.zoomFactor,
        fadeInDuration: 200
    };
    renderingParams = {
        ...renderingParams,
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
    var numLevels = graph.numLevels

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
        curLayer.setFetchingScheme("dbox", false);
        //curLayer.setFetchingScheme("tiling");

        curLayer.addPlacement({
            centroid_x: "con:0",
            centroid_y: "con:0",
            width: "con:0",
            height: "con:0"
        });

    }
}

module.exports = {
    addGraph
};