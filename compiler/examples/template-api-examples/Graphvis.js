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
        db: "coauthor_graph",
        queryNodes: "select * from nodes",
        queryEdges: "select * from edges"
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
// p.saveProject();
