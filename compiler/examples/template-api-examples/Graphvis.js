// libraries
const Project = require("../../src/index").Project;
const Graph = require("../../src/template-api/Graph").Graph;
//const renderers = require("../nba/renderers");

// construct a project
var p = new Project("coauthor_graph", "../../../config.txt");
// p.addRenderingParams(renderers.renderingParams);
// p.addStyles("../nba/nba.css");

// set up graph
var graph = {
    data: {
        db: "coauthor_graph",
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
            clusterLevels: [2000, 500, 50],
            randomState: 0,
            algorithm: "elkan"
        },
        encoding: {
            nodeSize: "memberNodeCount"
        },
        hover: {
            tooltip: {
                nodecolumns: ["authorname", "affiliation", "papercount", "coauthorcount", "membernodecount"],
                nodealiases: ["Name", "Affiliation", "Paper count", "Coauthor count", "Member Node count"],
                edgecolumns: ["author1", "author2", "papercount"],
                edgealiases: ["Author1", "Author2", "Paper count"]
            }
        }
    },
    config: {
        projectName: "coauthor_graph"
    }
};

p.addGraph(new Graph(graph));
p.saveProject();
