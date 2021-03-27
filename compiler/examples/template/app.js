// libraries
const Project = require("../../src/index").Project;
const Graph = require("../../src/template-api/Graph").Graph;
//const renderers = require("../nba/renderers");

// construct a project
var p = new Project("graphvis", "../../../config.txt");
// p.addRenderingParams(renderers.renderingParams);
// p.addStyles("../nba/nba.css");

// set up graph
var graph = {
    data: {
        db: "graphvis",
        queryNodes: "select * from authornodes",
        queryEdges: "select * from authoredges"
    },
    layout: {
        name: "openORD",
        maxLevel: 2,
        startLevel: 1,
        lastCut: 0.8,
        refineCut: 0.5,
        finalCut: 0.5
    },
    marks: {
        cluster: {
            aggregate: {
                measures: {
                    fields: ["memberNodeCount", "paperCount"],
                    function: "sum"
                }
            },
            numClusters: [200, 100, 40],
            randomState: 0,
            algorithm: "elkan"
        },
        encoding: {
            nodeSize: "memberNodeCount"
        },
        hover: {
            rankList: {
                mode: "tabular",
                fields: ["name", "affiliation", "paperCount", "memberNodeCount"],
                topk: 3,
                orientation: "vertical"
            },
            boundary: "convexhull"
        }
    },
    config: {
        projectName: "authorGraph"
    }
};

p.addGraph(new Graph(graph));
p.saveProject();


/*
// libraries
const Project = require("../../src/index").Project;
const Canvas = require("../../src/Canvas").Canvas;
const Jump = require("../../src/Jump").Jump;
const Layer = require("../../src/Layer").Layer;
const View = require("../../src/View").View;
const Graph = require("../../src/template-api/Graph").Graph;

// project components
const renderers = require("./renderers");
const transforms = require("./transforms");
const placements = require("./placements");

// definition of projects, views, canvases, layers and jumps

var width = 960 * 2;
var height = 500 * 2;

// construct a project
//var project = new Project("testing", "../../../config.txt");
//project.addRenderingParams(renderers.renderingParams);
//project.addStyles("../nba/nba.css");

// construct a project
var p = new Project("graphvis", "../../../config.txt");
// p.addRenderingParams(renderers.renderingParams);
// p.addStyles("../nba/nba.css");

// set up graph
var graph = {
    data: {
        db: "graphvis",
        queryNodes: "select * from authornodes",
        queryEdges: "select * from authoredges"
    },
    layout: {
        name: "openORD",
        maxLevel: 2,
        startLevel: 1,
        lastCut: 0.8,
        refineCut: 0.5,
        finalCut: 0.5
    },
    marks: {
        cluster: {
            aggregate: {
                measures: {
                    fields: ["memberNodeCount", "paperCount"],
                    function: "sum"
                }
            },
            numClusters: [200, 100, 40],
            randomState: 0,
            algorithm: "elkan"
        },
        encoding: {
            nodeSize: "memberNodeCount"
        },
        hover: {
            rankList: {
                mode: "tabular",
                fields: ["name", "affiliation", "paperCount", "memberNodeCount"],
                topk: 3,
                orientation: "vertical"
            },
            boundary: "convexhull"
        }
    },
    config: {
        projectName: "authorGraph"
    }
};

p.addGraph(new Graph(graph));
p.saveProject();

// ================== canvas ===================
/*
var testingCanvas = new Canvas("canvas", width, height);
project.addCanvas(testingCanvas);

// layer
var testingLayer = new Layer(transforms.emptyTransform, false);
testingCanvas.addLayer(testingLayer);
//stateBoundaryLayer.addRenderingFunc(renderers.test);
//testingLayer.addRenderingFunc(renderers.test);
testingLayer.addPlacement({
    centroid_x: "full",
    centroid_y: "full",
    width: "full",
    height: "full"
});

var view = new View("testing", 960*2, 500*2);
project.addView(view);
//project.setInitialStates(view, testingCanvas, 0, 0);



project.saveProject();

*/

