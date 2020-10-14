const Transform = require("../../src/Transform").Transform;

// data transforms...
var recfutTransform = new Transform(
    "SELECT * FROM facilities LIMIT 10000",
    "recfut",
    ""
    /*function(row) {
        var lat = row[4];
        var lng = row[5];
        var x = (int) (((960 * 2)/360.0) * (180 + lng)); //(960*2) is width
        var y = (int) (((500 * 2)/180.0) * (90 - lat)); //(500*2) is height
        var ret = [];
        ret.push(x);
        ret.push(y);
        ret.push(row[0]);
        ret.push(row[1]);
        ret.push(row[2]);
        ret.push(row[3]);
        ret.push(row[4]);
        ret.push(row[5]);
        


        return Java.to(ret, "java.lang.String[]");
    }*/,
    ["sid", "rfId", "type", "name", "lat", "lng"],
    true
);

module.exports = {
    recfutTransform
};
