const Transform = require("../../src/Transform").Transform;

// data transforms...
var nodeTransform = new Transform(
    "SELECT * FROM fbfriendsNodes",
    "graphvis",
    function(row) {
        var posX = row[2];
        var posY = row[3];
        var x = Math.round(posX * 1920/32 + 960); //(int) (((960 * 2)/360.0) * (180 + lng)); //(960*2) is width
        var y = Math.round((posY - 11.04) * 1080/14.64 + 540); //(int) (((500 * 2)/180.0) * (90 - lat)); //(500*2) is height
        var ret = [];
        ret.push(row[0]);
        ret.push(row[1]);
        ret.push(x);
        ret.push(y);
        
        return Java.to(ret, "java.lang.String[]");
    },
    ["nodeId", "edges", "x", "y"],
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

        var x1 = Math.round(posx1 * 1920/32 + 960);
        var y1 = Math.round((posy1 - 11.04) * 1080/14.64 + 540);
        var x2 = Math.round(posx2 * 1920/32 + 960);
        var y2 = Math.round((posy2 - 11.04) * 1080/14.64 + 540);

        var ret = [];
        ret.push(row[0]);
        ret.push(row[1]);
        ret.push(x1);
        ret.push(y1);
        ret.push(x2);
        ret.push(y2);

        return Java.to(ret, "java.lang.String[]");
    },
    ["edgeId", "timestamp", "x1", "y1", "x2", "y2"],
    true
);

module.exports = {
    nodeTransform,
    linkTransform
};
