const Transform = require("../../src/Transform").Transform;

// data transforms...

var emptyTransform = new Transform(
    "", //select * from teams;
    "", //nba
    "",
    [], //"id", "x", "y", "team_id", "city", "name", "abbr"
    true
);

module.exports = {
    emptyTransform
};
