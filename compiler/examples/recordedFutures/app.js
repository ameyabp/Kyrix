// libraries
const Project = require("../../src/index").Project;
const Canvas = require("../../src/Canvas").Canvas;
const Jump = require("../../src/Jump").Jump;
const Layer = require("../../src/Layer").Layer;
const View = require("../../src/View").View;
const SSV = require("../../src/template-api/SSV").SSV;

// project components
const renderers = require("./renderers");
const transforms = require("./transforms");
const placements = require("./placements");
const geomstrs = require("./geomstrs");

// definition of projects, views, canvases, layers and jumps

// construct a project
var project = new Project("recordedFutures", "../../../config.txt");
project.addRenderingParams(renderers.renderingParams);
//project.addRenderingParams(geomstrs.geomstrs);


// set up SSV
var width = 960 * 2;
var height = 500 * 2;

// ================== state map canvas ===================
var stateMapCanvas = new Canvas("statemap", width, height);
project.addCanvas(stateMapCanvas);

// static legends layer
//var stateMapLegendLayer = new Layer(null, true);
//stateMapCanvas.addLayer(stateMapLegendLayer);
//stateMapLegendLayer.addRenderingFunc(renderers.stateMapLegendRendering);

// bar chart layer
// var barLayer = new Layer(transforms.barTransform, false);
// stateMapCanvas.addLayer(barLayer);
// barLayer.addRenderingFunc(renderers.barRendering);
// barLayer.addPlacement({
//     centroid_x: "full",
//     centroid_y: "full",
//     width: "full",
//     height: "full"
// });

// state boundary layer
var stateBoundaryLayer = new Layer(transforms.recfutTransform, false);
stateMapCanvas.addLayer(stateBoundaryLayer);
//stateBoundaryLayer.addRenderingFunc(renderers.test);
stateBoundaryLayer.addRenderingFunc(renderers.test);
stateBoundaryLayer.addPlacement({
    centroid_x: "full",
    centroid_y: "full",
    width: "full",
    height: "full"
});

// stateBoundaryLayer.addTooltip(
//     ["state", "total_fire_size"],
//     ["State", "Acres burned"]
// );

var view = new View("facilities", 0, 0, width, height);
project.addView(view);
project.setInitialStates(view, stateMapCanvas, 0, 0);


var ssv = {
    data: {
        db: "recfut",
        query: "SELECT sid, rfId, type, name, latitude, longitude FROM mini_facilities;"
        //columnNames: ["sid", "rfId", "type", "name", "kyrix_geo_y", "kyrix_geo_x"]
    },
    layout: {
        x: {
            field: "longitude"
        },
        y: {
            field: "latitude"
        },
        z: {
            field: "sid",
            order: "desc"
        },
        geo: {
            level: 7,
            center: [39.5, -98.5]
        }
    },
    marks: {
        cluster: {
            mode: "circle"
        },
        hover: {
            rankList: {
                mode: "tabular",
                topk: 3,
                fields: ["sid", "rfId", "type", "name"],
                orientation: "vertical",
                boundary: "convexhull"
            }
        }
    },
    config: {
        numLevels: 10,
        topLevelWidth: width * 4,
        topLevelHeight: height * 4
    }
};

var ret = project.addSSV(new SSV(ssv), {view: view});



project.addJump(new Jump(stateMapCanvas, ret.pyramid[0], "literal_zoom_in"));
project.addJump(new Jump(ret.pyramid[0], stateMapCanvas, "literal_zoom_out"));

project.saveProject();