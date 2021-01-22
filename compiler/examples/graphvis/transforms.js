const Transform = require("../../src/Transform").Transform;

var nodeTransformc0 = new Transform(
    // no clustering - render only the level 0 nodes
    "SELECT * FROM authorNodes WHERE clusterLevel = 0",
    "graphvis",
    function(row, width, height) {
        // nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel
        var posX = row[1];
        var posY = row[2];
        //var x = Math.round((posX -(- 1))/(1 -(-1)) * 1920);
        //var z = Math.round((posX+1)/2 * 1920);
        var x = Math.round(posX * width);
        var y = Math.round(posY * height);
        var ret = [];
        ret.push(row[0]);
        ret.push(x);
        ret.push(y);
        ret.push(row[3]);
        ret.push(row[4]);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);
        
        return Java.to(ret, "java.lang.String[]");
    },
    ["nodeId", "x", "y", "authorName", "affiliation", "paperCount", "coauthorCount", "memberNodeCount", "clusterLevel"],
    true
);

var linkTransformc0 = new Transform(
    // no clustering, render only the level 0 edges
    "SELECT * FROM authorEdges WHERE clusterLevel = 0",
    "graphvis",
    function(row, width, height) {
        // edgeId, x1, y1, x2, y2, author1, author2, paperCount, isMetaEdge
        var posx1 = row[1];
        var posy1 = row[2];
        var posx2 = row[3];
        var posy2 = row[4];

        var x1 = Math.round(posx1 * width);
        var y1 = Math.round(posy1 * height);
        var x2 = Math.round(posx2 * width);
        var y2 = Math.round(posy2 * height);

        var centroidx = Math.round((x1 + x2)/2);
        var centroidy = Math.round((y1 + y2)/2);
        var bbwidth = Math.abs(x2-x1);
        var bbheight = Math.abs(y2-y1);

        var ret = [];
        ret.push(row[0]);
        ret.push(x1);
        ret.push(y1);
        ret.push(x2);
        ret.push(y2);
        ret.push(centroidx);
        ret.push(centroidy);
        ret.push(bbwidth);
        ret.push(bbheight);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);

        return Java.to(ret, "java.lang.String[]");
    },
    ["edgeId", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight", "author1", "author2", "paperCount", "clusterLevel"],
    true
);

// data transforms...
var nodeTransformc1 = new Transform(
    // one level of clustering
    "SELECT * FROM authorNodes WHERE clusterLevel = 1",
    "graphvis",
    function(row, width, height) {
        // nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel
        var posX = row[1];
        var posY = row[2];
        //var x = Math.round((posX -(- 1))/(1 -(-1)) * 1920);
        //var z = Math.round((posX+1)/2 * 1920);
        var x = Math.round(posX * width);
        var y = Math.round(posY * height);
        var ret = [];
        ret.push(row[0]);
        ret.push(x);
        ret.push(y);
        ret.push(row[3]);
        ret.push(row[4]);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);
        
        return Java.to(ret, "java.lang.String[]");
    },
    ["nodeId", "x", "y", "authorName", "affiliation", "paperCount", "coauthorCount", "memberNodeCount", "clusterLevel"],
    true
);

var linkTransformc1 = new Transform(
    // one level of clustering
    "SELECT * FROM authorEdges WHERE clusterLevel = 1",
    "graphvis",
    function(row, width, height) {
        // edgeId, x1, y1, x2, y2, author1, author2, paperCount, clusterLevel
        var posx1 = row[1];
        var posy1 = row[2];
        var posx2 = row[3];
        var posy2 = row[4];

        var x1 = Math.round(posx1 * width);
        var y1 = Math.round(posy1 * height);
        var x2 = Math.round(posx2 * width);
        var y2 = Math.round(posy2 * height);

        var centroidx = Math.round((x1 + x2)/2);
        var centroidy = Math.round((y1 + y2)/2);
        var bbwidth = Math.abs(x2-x1);
        var bbheight = Math.abs(y2-y1);

        var ret = [];
        ret.push(row[0]);
        ret.push(x1);
        ret.push(y1);
        ret.push(x2);
        ret.push(y2);
        ret.push(centroidx);
        ret.push(centroidy);
        ret.push(bbwidth);
        ret.push(bbheight);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);

        return Java.to(ret, "java.lang.String[]");
    },
    ["edgeId", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight", "author1", "author2", "paperCount", "clusterLevel"],
    true
);

// data transforms...
var nodeTransformc2 = new Transform(
    // second level of clustering
    "SELECT * FROM authorNodes WHERE clusterLevel = 2",
    "graphvis",
    function(row, width, height) {
        // nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel
        var posX = row[1];
        var posY = row[2];
        //var x = Math.round((posX -(- 1))/(1 -(-1)) * 1920);
        //var z = Math.round((posX+1)/2 * 1920);
        var x = Math.round(posX * width);
        var y = Math.round(posY * height);
        var ret = [];
        ret.push(row[0]);
        ret.push(x);
        ret.push(y);
        ret.push(row[3]);
        ret.push(row[4]);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);
        
        return Java.to(ret, "java.lang.String[]");
    },
    ["nodeId", "x", "y", "authorName", "affiliation", "paperCount", "coauthorCount", "memberNodeCount", "clusterLevel"],
    true
);

var linkTransformc2 = new Transform(
    // second level of clustering
    "SELECT * FROM authorEdges WHERE clusterLevel = 2",
    "graphvis",
    function(row, width, height) {
        // edgeId, x1, y1, x2, y2, author1, author2, paperCount, isMetaEdge
        var posx1 = row[1];
        var posy1 = row[2];
        var posx2 = row[3];
        var posy2 = row[4];

        var x1 = Math.round(posx1 * width);
        var y1 = Math.round(posy1 * height);
        var x2 = Math.round(posx2 * width);
        var y2 = Math.round(posy2 * height);

        var centroidx = Math.round((x1 + x2)/2);
        var centroidy = Math.round((y1 + y2)/2);
        var bbwidth = Math.abs(x2-x1);
        var bbheight = Math.abs(y2-y1);

        var ret = [];
        ret.push(row[0]);
        ret.push(x1);
        ret.push(y1);
        ret.push(x2);
        ret.push(y2);
        ret.push(centroidx);
        ret.push(centroidy);
        ret.push(bbwidth);
        ret.push(bbheight);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);

        return Java.to(ret, "java.lang.String[]");
    },
    ["edgeId", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight", "author1", "author2", "paperCount", "clusterLevel"],
    true
);

// data transforms...
var nodeTransformc3 = new Transform(
    // second level of clustering
    "SELECT * FROM authorNodes WHERE clusterLevel = 3",
    "graphvis",
    function(row, width, height) {
        // nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel
        var posX = row[1];
        var posY = row[2];
        //var x = Math.round((posX -(- 1))/(1 -(-1)) * 1920);
        //var z = Math.round((posX+1)/2 * 1920);
        var x = Math.round(posX * width);
        var y = Math.round(posY * height);
        var ret = [];
        ret.push(row[0]);
        ret.push(x);
        ret.push(y);
        ret.push(row[3]);
        ret.push(row[4]);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);
        
        return Java.to(ret, "java.lang.String[]");
    },
    ["nodeId", "x", "y", "authorName", "affiliation", "paperCount", "coauthorCount", "memberNodeCount", "clusterLevel"],
    true
);

var linkTransformc3 = new Transform(
    // second level of clustering
    "SELECT * FROM authorEdges WHERE clusterLevel = 3",
    "graphvis",
    function(row, width, height) {
        // edgeId, x1, y1, x2, y2, author1, author2, paperCount, isMetaEdge
        var posx1 = row[1];
        var posy1 = row[2];
        var posx2 = row[3];
        var posy2 = row[4];

        var x1 = Math.round(posx1 * width);
        var y1 = Math.round(posy1 * height);
        var x2 = Math.round(posx2 * width);
        var y2 = Math.round(posy2 * height);

        var centroidx = Math.round((x1 + x2)/2);
        var centroidy = Math.round((y1 + y2)/2);
        var bbwidth = Math.abs(x2-x1);
        var bbheight = Math.abs(y2-y1);

        var ret = [];
        ret.push(row[0]);
        ret.push(x1);
        ret.push(y1);
        ret.push(x2);
        ret.push(y2);
        ret.push(centroidx);
        ret.push(centroidy);
        ret.push(bbwidth);
        ret.push(bbheight);
        ret.push(row[5]);
        ret.push(row[6]);
        ret.push(row[7]);
        ret.push(row[8]);

        return Java.to(ret, "java.lang.String[]");
    },
    ["edgeId", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight", "author1", "author2", "paperCount", "clusterLevel"],
    true
);

module.exports = {
    nodeTransformc0,
    linkTransformc0,
    nodeTransformc1,
    linkTransformc1,
    nodeTransformc2,
    linkTransformc2,
    nodeTransformc3,
    linkTransformc3
};
