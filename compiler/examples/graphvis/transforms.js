const Transform = require("../../src/Transform").Transform;

// data transforms...
var nodeTransform = new Transform(
    "SELECT * FROM fbfriendsNodes",
    "graphvis",
    function(row) {
        var posX = row[2];
        var posY = row[3];
        var x = Math.round((posX + 1)/2 * 1920);
        var y = Math.round((posY - 3)/1 * 1080);
        var ret = [];
        ret.push(row[0]);
        ret.push(row[1]);
        ret.push(x);
        ret.push(y);
        
        return Java.to(ret, "java.lang.String[]");
    },
    ["nodeId", "edgeCount", "x", "y"],
    true
);

var linkTransform = new Transform(
    "SELECT * FROM fbfriendsEdges",
    "graphvis",
    function(row) {
        var posx1 = row[2];
        var posy1 = row[3];
        var posx2 = row[4];
        var posy2 = row[5];

        var x1 = Math.round((posx1 + 1)/2 * 1920 + 960);
        var y1 = Math.round((posy1 - 3)/1 * 1080);
        var x2 = Math.round((posx2 + 1)/2 * 1920 + 960);
        var y2 = Math.round((posy2 - 3)/1 * 1080);

        var centroidx = (x1 + x2)/2;
        var centroidy = (y1 + y2)/2;
        var bbwidth = Math.abs(x2-x1);
        var bbheight = Math.abs(y2-y1);

        var ret = [];
        ret.push(row[0]);
        ret.push(row[1]);
        ret.push(x1);
        ret.push(y1);
        ret.push(x2);
        ret.push(y2);
        ret.push(centroidx);
        ret.push(centroidy);
        ret.push(bbwidth);
        ret.push(bbheight);

        return Java.to(ret, "java.lang.String[]");
    },
    ["edgeId", "timestamp", "x1", "y1", "x2", "y2", "centroidx", "centroidy", "bbwidth", "bbheight"],
    true
);

module.exports = {
    nodeTransform,
    linkTransform
};
