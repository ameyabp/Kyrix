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
        nodesCsv: "graphNodesData.csv",
        edgesCsv: "graphEdgesData.csv",
        db: "kyrix",
        queryNodes: "select _id, _x, _y, _level, _parentnode, _membernodes, _membernodecount, clusteragg from bbox_coauthor_graph_graph0_level0layer0",
        queryEdges: "select _id, _srcid, _dstid, _level, _weight, _parentedge, _memberedges, _memberedgecount, clusteragg, _x1, _x2, _y1, _y2 from bbox_coauthor_graph_graph0_level0layer1"
    },
    layout: {
        name: "openORD",
        ord_maxLevel: 2,
        ord_startLevel: 1,
        ord_lastCut: 0.8,
        ord_refineCut: 0.5,
        ord_finalCut: 0.5
    },
    summarization: {
        cluster: {
            aggregate: {
                nodes: {
                    fields: ["papers", "coauthors"],
                    functions: "count"
                },
                edges: {
                    fields: ["papers"],
                    functions: "count"
                }
            },
            clusterLevels: [1000, 200, 50],
            randomState: 0,
            algorithm: "kmeans"
        }
    },
    marks: {
        encoding: {
            nodeSize: "memberNodeCount",
            edgeThickness: "memberEdgeCount"
        },
        hover: {
            nodes: {
                rankList: {
                    mode: "tabular",
                    topk: 3,
                    fields: ["authorName", "affiliation", "papers", "coauthors"],
                    orderBy: "papers",
                    order: "desc"
                }
            },
            edges: {
                tooltip: {
                    columns: ["papers"],
                    aliases: ["Paper count"]
                }
            }
        }
    }
};

p.addGraph(new Graph(graph));
p.saveProject();
