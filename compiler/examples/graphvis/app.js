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
// one level of clustering
var bgCanvas1 = new Canvas("bgCanvas1", 1920, 1080);
p.addCanvas(bgCanvas1);

// node layer
var nodeLayer = new Layer(transforms.nodeTransformc1, false);
bgCanvas1.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacementc1);
nodeLayer.addRenderingFunc(renderers.nodeRenderingc1);

// link layer
var linkLayer = new Layer(transforms.linkTransformc1, false);
bgCanvas1.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacementc1);
linkLayer.addRenderingFunc(renderers.linkRenderingc1);

// ================== Canvas 2 ===================
// no clustering
var bgCanvas2 = new Canvas("bgCanvas2", 3840, 2160);
p.addCanvas(bgCanvas2);

// node layer
var nodeLayer = new Layer(transforms.nodeTransformc2, false);
bgCanvas2.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacementc2);
nodeLayer.addRenderingFunc(renderers.nodeRenderingc2);

// link layer
var linkLayer = new Layer(transforms.linkTransformc2, false);
bgCanvas2.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacementc2);
linkLayer.addRenderingFunc(renderers.linkRenderingc2);


// ================== Views ===================
var view = new View("graphvis", 0, 0, 1920, 1080);
p.addView(view);
p.setInitialStates(view, bgCanvas1, 0, 0);

// ================= Jumps ====================
var jumpIn = new Jump(bgCanvas1, bgCanvas2, "literal_zoom_in");
var jumpOut = new Jump(bgCanvas2, bgCanvas1, "literal_zoom_out");
p.addJump(jumpIn);
p.addJump(jumpOut);

// save to db
p.saveProject();
