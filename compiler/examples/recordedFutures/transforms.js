const Transform = require("../../src/Transform").Transform;

// data transforms...
var stateMapTransform = new Transform(
    "SELECT * FROM facilities",
    "recfut",
    "",
    ["sid", "rfId", "type", "name", "lat", "lng"],
    true
);

module.exports = {
    stateMapTransform
};
