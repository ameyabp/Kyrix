// libraries
const Project = require("../../src/index").Project;
const Canvas = require("../../src/Canvas").Canvas;
const Jump = require("../../src/Jump").Jump;
const Layer = require("../../src/Layer").Layer;
const View = require("../../src/View").View;

// project components
const renderers = require("./renderers");
const transforms = require("./transforms");
const placements = require("./placements");

// definition of projects, views, canvases, layers and jumps

var width = 960 * 2;
var height = 500 * 2;

// construct a project
var project = new Project("testing", "../../../config.txt");
project.addRenderingParams(renderers.renderingParams);
project.addStyles("../nba/nba.css");

// ================== canvas ===================
var testingCanvas = new Canvas("canvas", width, height);
project.addCanvas(testingCanvas);

// layer
var testingLayer = new Layer(transforms.emptyTransform, false);
testingCanvas.addLayer(testingLayer);
//stateBoundaryLayer.addRenderingFunc(renderers.test);
testingLayer.addRenderingFunc(renderers.test);
testingLayer.addPlacement({
    centroid_x: "full",
    centroid_y: "full",
    width: "full",
    height: "full"
});

var view = new View("testing", 960*2, 500*2);
project.addView(view);
project.setInitialStates(view, testingCanvas, 0, 0);



project.saveProject();