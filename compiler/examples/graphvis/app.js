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

// ================== Canvas 0 ===================
// base level - no clustering
var bgCanvas0 = new Canvas("bgCanvas0", 3840, 2160);
p.addCanvas(bgCanvas0);

// node layer
var nodeLayer = new Layer(transforms.nodeTransformc0, false);
bgCanvas0.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacementc0);
nodeLayer.addRenderingFunc(renderers.nodeRenderingc0);
nodeLayer.addTooltip(["authorName", "affiliation", "paperCount", "coauthorCount"], ["Name", "Affiliation", "Paper count", "Coauthor count"]);

// link layer
var linkLayer = new Layer(transforms.linkTransformc0, false);
bgCanvas0.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacementc0);
linkLayer.addRenderingFunc(renderers.linkRenderingc0);
linkLayer.addTooltip(["author1", "author2", "paperCount"], ["Author 1", "Author 2", "Paper count"]);

// ================== Canvas 1 ===================
// first level of clustering
var bgCanvas1 = new Canvas("bgCanvas1", 1920, 1080);
p.addCanvas(bgCanvas1);

// node layer
var nodeLayer = new Layer(transforms.nodeTransformc1, false);
bgCanvas1.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacementc1);
nodeLayer.addRenderingFunc(renderers.nodeRenderingc1);
nodeLayer.addTooltip(["authorName", "affiliation", "paperCount", "coauthorCount"], ["Name", "Affiliation", "Paper count", "Coauthor count"]);

// link layer
var linkLayer = new Layer(transforms.linkTransformc1, false);
bgCanvas1.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacementc1);
linkLayer.addRenderingFunc(renderers.linkRenderingc1);
linkLayer.addTooltip(["author1", "author2", "paperCount"], ["Author 1", "Author 2", "Paper count"]);

// ================== Canvas 2 ===================
// second level of clustering
var bgCanvas2 = new Canvas("bgCanvas2", 960, 540);
p.addCanvas(bgCanvas2);

// node layer
var nodeLayer = new Layer(transforms.nodeTransformc2, false);
bgCanvas2.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacementc2);
nodeLayer.addRenderingFunc(renderers.nodeRenderingc2);
nodeLayer.addTooltip(["authorName", "affiliation", "paperCount", "coauthorCount"], ["Name", "Affiliation", "Paper count", "Coauthor count"]);

// link layer
var linkLayer = new Layer(transforms.linkTransformc2, false);
bgCanvas2.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacementc2);
linkLayer.addRenderingFunc(renderers.linkRenderingc2);
linkLayer.addTooltip(["author1", "author2", "paperCount"], ["Author 1", "Author 2", "Paper count"]);

// ================== Canvas 3 ===================
// second level of clustering
var bgCanvas3 = new Canvas("bgCanvas3", 480, 270);
p.addCanvas(bgCanvas3);

// node layer
var nodeLayer = new Layer(transforms.nodeTransformc3, false);
bgCanvas3.addLayer(nodeLayer);
nodeLayer.addPlacement(placements.nodePlacementc3);
nodeLayer.addRenderingFunc(renderers.nodeRenderingc3);
nodeLayer.addTooltip(["authorName", "affiliation", "paperCount", "coauthorCount"], ["Name", "Affiliation", "Paper count", "Coauthor count"]);

// link layer
var linkLayer = new Layer(transforms.linkTransformc3, false);
bgCanvas3.addLayer(linkLayer);
linkLayer.addPlacement(placements.linkPlacementc3);
linkLayer.addRenderingFunc(renderers.linkRenderingc3);
linkLayer.addTooltip(["author1", "author2", "paperCount"], ["Author 1", "Author 2", "Paper count"]);

// ================== Views ===================
var view = new View("graphvis", 0, 0, 480, 270);
p.addView(view);
p.setInitialStates(view, bgCanvas3, 0, 0);

// ================= Jumps ====================
var jumpIn10 = new Jump(bgCanvas1, bgCanvas0, "literal_zoom_in");
var jumpOut01 = new Jump(bgCanvas0, bgCanvas1, "literal_zoom_out");
p.addJump(jumpIn10);
p.addJump(jumpOut01);

var jumpIn21 = new Jump(bgCanvas2, bgCanvas1, "literal_zoom_in");
var jumpOut12 = new Jump(bgCanvas1, bgCanvas2, "literal_zoom_out");
p.addJump(jumpIn21);
p.addJump(jumpOut12);

var jumpIn32 = new Jump(bgCanvas3, bgCanvas2, "literal_zoom_in");
var jumpOut23 = new Jump(bgCanvas2, bgCanvas3, "literal_zoom_out");
p.addJump(jumpIn32);
p.addJump(jumpOut23);

// save to db
p.saveProject();
