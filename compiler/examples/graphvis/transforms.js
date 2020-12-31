const Transform = require("../../src/Transform").Transform;

// data transforms...
var nodeTransformc1 = new Transform(
    // one level of clustering
    "SELECT * FROM authorNodes WHERE isMetaNode = true",
    "graphvis",
    function(row, width, height) {
        // nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, isMetaNode
        var posX = row[1];
        var posY = row[2];
        //var x = Math.round((posX -(- 1))/(1 -(-1)) * 1920);
        //var z = Math.round((posX+1)/2 * 1920);
        var x = Math.round((posX -(- 52.84)) / (65.19 -(- 52.84)) * width);
        var y = Math.round((posY -(- 62.02)) / (51.98 -(- 62.02)) * height);
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
    ["nodeId", "x", "y", "authorName", "affiliation", "paperCount", "coauthorCount", "memberNodeCount", "isMetaNode"],
    true
);

var nodeTransformc2 = new Transform(
    // no clustering
    "SELECT * FROM authorNodes",
    "graphvis",
    function(row, width, height) {
        // nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, isMetaNode
        var posX = row[1];
        var posY = row[2];
        //var x = Math.round((posX -(- 1))/(1 -(-1)) * 1920);
        //var z = Math.round((posX+1)/2 * 1920);
        var x = Math.round((posX -(- 52.84)) / (65.19 -(- 52.84)) * width);
        var y = Math.round((posY -(- 62.02)) / (51.98 -(- 62.02)) * height);
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
    ["nodeId", "x", "y", "authorName", "affiliation", "paperCount", "coauthorCount", "memberNodeCount", "isMetaNode"],
    true
);

var linkTransformc1 = new Transform(
    // one level of clustering
    "SELECT * FROM authorEdges WHERE isMetaEdge = true",
    "graphvis",
    function(row, width, height) {
        // edgeId, x1, y1, x2, y2, author1, author2, paperCount, isMetaEdge
        var posx1 = row[1];
        var posy1 = row[2];
        var posx2 = row[3];
        var posy2 = row[4];

        var x1 = Math.round((posx1 -(- 52.84)) / (65.19 -(- 52.84)) * width);
        var y1 = Math.round((posy1 -(- 62.02)) / (51.98 -(- 62.02)) * height);
        var x2 = Math.round((posx2 -(- 52.84)) / (65.19 -(- 52.84)) * width);
        var y2 = Math.round((posy2 -(- 62.02)) / (51.98 -(- 62.02)) * height);

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
    ["edgeId", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight", "author1", "author2", "paperCount", "isMetaEdge"],
    true
);

var linkTransformc2 = new Transform(
    // no clustering
    "SELECT * FROM authorEdges WHERE isMetaEdge = false",
    "graphvis",
    function(row, width, height) {
        // edgeId, x1, y1, x2, y2, author1, author2, paperCount, isMetaEdge
        var posx1 = row[1];
        var posy1 = row[2];
        var posx2 = row[3];
        var posy2 = row[4];

        var x1 = Math.round((posx1 -(- 52.84)) / (65.19 -(- 52.84)) * width);
        var y1 = Math.round((posy1 -(- 62.02)) / (51.98 -(- 62.02)) * height);
        var x2 = Math.round((posx2 -(- 52.84)) / (65.19 -(- 52.84)) * width);
        var y2 = Math.round((posy2 -(- 62.02)) / (51.98 -(- 62.02)) * height);

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
    ["edgeId", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight", "author1", "author2", "paperCount", "isMetaEdge"],
    true
);

module.exports = {
    nodeTransformc1,
    linkTransformc1,
    nodeTransformc2,
    linkTransformc2
};
