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

// construct a project
var p = new Project("graphvis", "../../../config.txt");
p.addRenderingParams(renderers.renderingParams);

// ================== Canvas 1 ===================
var bgCanvas = new Canvas("bgCanvas", 1920, 1080);
p.addCanvas(bgCanvas);

// node layer
var nodeLayer = new Layer(transforms.nodeTransform, false);
bgCanvas.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacement);
nodeLayer.addRenderingFunc(renderers.nodeRendering);

// link layer
var linkLayer = new Layer(transforms.linkTransform, false);
bgCanvas.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacement);
linkLayer.addRenderingFunc(renderers.linkRendering);

// ================== Views ===================
var view = new View("graphvis", 200, 200, 960, 540);
p.addView(view);
p.setInitialStates(view, bgCanvas, 0, 0);

// save to db
p.saveProject();
