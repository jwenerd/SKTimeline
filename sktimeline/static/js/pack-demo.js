// static/js/pack-demo.js
"use strict";

var PACK_DATA = {
  name: "pack",
  children: [
    {
      name: "A",
      children: [
        {"name": "please", "size": 240},
        {"name": "thanks", "size": 1001},
        {"name": "yes", "size": 393 }
      ]
    },
    {
      name: "B",
      children: [
        {"name": "no", "size": 140 },
        {"name": "nadda", "size": 330 },
        {"name": "neither", "size": 400 },
        {"name": "dot", "size": 30 },
        {"name": "dilly", "size": 20 },
        {
          name: "C",
          children: [
            {"name": "wow", "size": 200 },
            {"name": "amazing", "size": 100 },
          ]
        }
      ]
    }
  ]
}
console.log(PACK_DATA);

(function(){
  var node,
      root,
      $e = $('#pack'),
      w = $e.width(),
      h = $e.height(),
      r = parseInt( w * 9 / 16 , 10 ),
      x = d3.scale.linear().range([0, r]),
      y = d3.scale.linear().range([0, r]);
  
  var pack = d3.layout.pack()
                      .size([r, r])
                      .value(function(d) { return d.size; });

  var vis = d3.select( $e.get(0) ).insert("svg:svg")
                      .attr("width", w)
                      .attr("height", h)
                      .append("svg:g")
                      .attr("transform", "translate(" + (w - r) / 2 + "," + (h - r) / 2 + ")");
  
  
  node = root = PACK_DATA;
  var nodes = pack.nodes(root);
  vis.selectAll("circle")
      .data(nodes)
    .enter().append("svg:circle")
      .attr("class", function(d) { return d.children ? "parent" : "child"; })
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", function(d) { return d.r; })
      .on("click", function(d) { return zoom(node == d ? root : d); });

  vis.selectAll("text")
      .data(nodes)
    .enter().append("svg:text")
      .attr("class", function(d) { return d.children ? "parent" : "child"; })
      .attr("x", function(d) { return d.x; })
      .attr("y", function(d) { return d.y; })
      .attr("dy", ".35em")
      .attr("text-anchor", "middle")
      .style("opacity", function(d) { return d.r > 20 ? 1 : 0; })
      .text(function(d) { return d.name; });

  d3.select(window).on("click", function() { zoom(root); });
  
  function zoom(d, i) {
    var k = r / d.r / 2;
    x.domain([d.x - d.r, d.x + d.r]);
    y.domain([d.y - d.r, d.y + d.r]);
  
    var t = vis.transition()
        .duration(d3.event.altKey ? 7500 : 750);
  
    t.selectAll("circle")
        .attr("cx", function(d) { return x(d.x); })
        .attr("cy", function(d) { return y(d.y); })
        .attr("r", function(d) { return k * d.r; });
  
    t.selectAll("text")
        .attr("x", function(d) { return x(d.x); })
        .attr("y", function(d) { return y(d.y); })
        .style("opacity", function(d) { return k * d.r > 20 ? 1 : 0; });
  
    node = d;
    d3.event.stopPropagation();
  }
})();