/*
    Contains some commonly used tools for working
    with d3.js
*/

var stars_fill_colors = [    
    "#0080CF", "#00BCE4",
    "#6BBC49", "#CEDC45",
    "#5160AB", "#A486BD"
]
    // "#a9ad70", "#aa9882", "#b1adac", "#bfb18e",
var stars_stroke_colors = [
	"#15387F", "#15387F",
	"#00A060", "#00A060", 
	"#3C2985", "#3C2985"
];

stars_fill = function() {
    return d3.scale.ordinal().range(stars_fill_colors);
};

stars_stroke = function() {
    return d3.scale.ordinal().range(stars_stroke_colors);
};

function tweenOpacity(o) {
return function(d, i, a) {
    return d3.interpolate(a, o)
}
}