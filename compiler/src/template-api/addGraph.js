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

    console.log("----- Adding graph object to project-------");
}

module.exports = {
    addGraph
};