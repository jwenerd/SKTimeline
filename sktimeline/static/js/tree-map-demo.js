// static/js/tree-map-demo.js
"use strict";

function formatEntityData(ent_counts){
  var data = { name: 'entities', children: [] },
      labels = Object.keys(ent_counts);
  
  for (var i = 0; i < labels.length; i++){
    var label = labels[i],
        child = { name: label, children: [] };

    child['children'] = ent_counts[label].map(function(ent_datum){
      return { name: ent_datum[0], size: ent_datum[1] };
    });
    data['children'].push(child);
  }

  return data;
}
// GPL code adapted from https://bl.ocks.org/mbostock/raw/4063582/ 
(function(ent_counts) {
  var $ele = $('#tree-map'),
      $svg = $ele.find('svg'),
      width = $ele.width(),
      height = 600,
      treedata = formatEntityData(ent_counts);

  console.log(treedata);
  window.treedata = treedata;
  $svg.attr('width', width);

  var svg = d3.select('#tree-map svg');

  var fader = function(color) { return d3.interpolateRgb(color, "#fff")(0.2); },
      color = d3.scaleOrdinal(d3.schemeCategory20.map(fader)),
      format = d3.format(",d");

  var treemap = d3.treemap()
         .tile(d3.treemapResquarify)
         .size([width, height])
         .round(true)
         .paddingInner(1);

  var root = d3.hierarchy(treedata)
         .eachBefore(function(d) { d.data.id = (d.parent ? d.parent.data.id + "." : "") + d.data.name; })
         .sum( sumBySize )
         .sort(function(a, b) { return b.height - a.height || b.value - a.value; });
   
    treemap(root);
   
  var cell = svg.selectAll("g")
    .data(root.leaves())
    .enter().append("g")
        .attr("transform", function(d) { return "translate(" + d.x0 + "," + d.y0 + ")"; });

  cell.append("rect")
    .attr("id", function(d) { return d.data.id; })
    .attr("width", function(d) { return d.x1 - d.x0; })
    .attr("height", function(d) { return d.y1 - d.y0; })
    .attr("fill", function(d) { return color(d.parent.data.id); });

  cell.append("clipPath")
    .attr("id", function(d) { return "clip-" + d.data.id; })
    .append("use")
    .attr("xlink:href", function(d) { return "#" + d.data.id; });

  cell.append("text")
    .attr("clip-path", function(d) { return "url(#clip-" + d.data.id + ")"; })
    .selectAll("tspan")
       .data(function(d) { return d.data.name.split(/(?=[A-Z][^A-Z])/g); })
    .enter().append("tspan")
      .attr("x", 4)
      .attr("y", function(d, i) { return 13 + i * 10; })
      .text(function(d) { return d; });

  cell.append("title")
    .text(function(d) { return d.data.id + "\n" + format(d.value); });


  d3.selectAll("input[name='mode']")
      .data([sumBySize, sumByCount], function(d) { return d ? d.name : this.value; })
      .on("change", changed);
  
  function changed(sum) {

    treemap(root.sum(sum));

    cell.transition()
        .duration(750)
        .attr("transform", function(d) { return "translate(" + d.x0 + "," + d.y0 + ")"; })
      .select("rect")
        .attr("width", function(d) { return d.x1 - d.x0; })
        .attr("height", function(d) { return d.y1 - d.y0; });
  }

  function sumByCount(d) {
    return d.children ? 0 : 1;
  }
  
  function sumBySize(d) {
    return d.size;
  }


})(window.ent_counts);