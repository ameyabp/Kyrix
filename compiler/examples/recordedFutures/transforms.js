const Transform = require("../../src/Transform").Transform;

// data transforms...
var stateMapTransform = new Transform(
    "SELECT * FROM facilities",
    "recfut",
    "",
    [],
    true
);

module.exports = {
    stateMapTransform
};
