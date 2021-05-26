// libraries
const Project = require("../../src/index").Project;
const Graph = require("../../src/template-api/Graph").Graph;
//const renderers = require("../nba/renderers");

// construct a project
var p = new Project("facebook_large", "../../../config.txt");
// p.addRenderingParams(renderers.renderingParams);
// p.addStyles("../nba/nba.css");

// set up graph
var graph = {
    data: {
        nodesCsv: "musae_facebook_target.csv",
        edgesCsv: "musae_facebook_edges.csv",
        db: "kyrix",
        queryNodes: "select _id, _x, _y, _level, _parentnode, _membernodes, _membernodecount, clusteragg from bbox_facebook_large_graph0_level0layer0",
        queryEdges: "select _id, _srcid, _dstid, _level, _weight, _parentedge, _memberedges, _memberedgecount, clusteragg, _x1, _x2, _y1, _y2 from bbox_facebook_large_graph0_level0layer1"
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
            // aggregate: {
            //     nodes: {
            //         fields: ["page_name", "page_type"],
            //         functions: "count"
            //     }
            // },
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
                    fields: ["page_name", "page_type", "facebook_id"],
                    orderBy: "facebook_id",
                    order: "asc"
                }
                // tooltip: {
                //     columns: ["page_name", "page_type"],
                //     aliases: ["Page Name", "Page Type"]
                // }
            },
            edges: {
                tooltip: {
                    columns: ["memberEdgeCount"],
                    aliases: ["Number of edges"]
                }
            }
        }
    }
};

p.addGraph(new Graph(graph));
p.saveProject();
