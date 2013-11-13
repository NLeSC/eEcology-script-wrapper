## -- encoding: utf-8 -
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
    <script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.3.9/d3.min.js" charset="utf-8"></script>
    <style type="text/css">

body {
  padding-top: 20px;
}

svg {
  font-size: 22px;
  shape-rendering: crispEdges;
}

.day {
  fill: #fff;
  stroke: #000;
  stroke-opacity: .1;
}

.month {
  fill: none;
  stroke: #000;
  stroke-width: 2px;
}

.year {
   display: block;
}

#years {
  text-align: center;
}

#legend {
  float: right;
}

    </style>
  </head>
  <body>
        <div id="legend"></div>
      <div id="header">
        <div>Tracker: ${tracker_id}</div>
        <span>Time range: ${start} - ${end}</span>
      </div>
      <div id="footer">
        <div class="hint">Use the pulldown to change shown metric</div>
        <div><select>
          <option  value="fixes">Nr. of GPS fixes</option>
          <option  value="maxalt">Maximum altitude (m)</option>
          <option  value="minalt">Minimum altitude (m)</option>
          <option  value="maxtemp">Maximum temperature (&deg;C)</option>
          <option  value="mintemp">Minimum temperature (&deg;C)</option>
          <option  value="maxpres">Maximum pressure</option>
          <option  value="minpres">Minimum pressure</option>
          <option  value="distance">2D Distance travelled (km)</option>
        </select></div>
        <div>Mouse over day to see date and value.</div>
        <div id="years"></div>
      </div>
    <script type="text/javascript">

var m = [29, 20, 60, 19], // top right bottom left margin
    w = 1420 - m[1] - m[3], // width
    h = 200 - m[0] - m[2], // height
    z = 22; // cell size

var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    month = d3.time.format("%B"),
    percent = d3.format(".1%"),
    data,
    formatDate = d3.time.format("%Y-%m-%d"),
    formatNumber = d3.format(",d"),
    formatPercent = d3.format("+.1%");

var year_range = d3.range(${start.year}, ${end.year}+1);

var svg = d3.select("#years").selectAll(".year")
    .data(year_range)
  .enter().append("div")
    .attr("class", "year")
    .style("width", w + m[1] + m[3] + "px")
    .style("height", h + m[0] + m[2] + "px")
    .style("display", "inline-block")
  .append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + (m[3] + (w - z * 53) / 2) + "," + (m[0] + (h - z * 7) / 2) + ")");

svg.append("svg:text")
    .attr("transform", "translate(-6," + z * 3.5 + ")rotate(-90)")
    .attr("text-anchor", "middle")
    .text(String);

var rect = svg.selectAll("rect.day")
    .data(function(d) { return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("svg:rect")
    .attr("class", "day")
    .attr("width", z)
    .attr("height", z)
    .attr("x", function(d) { return week(d) * z; })
    .attr("y", function(d) { return day(d) * z; })
    ;

rect.append("svg:title");

svg.selectAll("path.month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("svg:path")
    .attr("class", "month")
    .attr("d", monthPath)
;

d3.select("select").on("change", function() {
    display(this.value);
});

d3.csv('${csv}', function(csv) {

  data = d3.nest()
      .key(function(d) { return (d.date = formatDate.parse(d.date)).getFullYear(); })
      .key(function(d) { return d.date; })
      .rollup(function(d) {
          return {
              'fixes': +d[0]['fixes'],
              'maxalt': +d[0]['maxalt'],
              'minalt': +d[0]['minalt'],
              'maxtemp': +d[0]['maxtemp'],
              'mintemp': +d[0]['mintemp'],
              'maxpres': +d[0]['maxpres'],
              'minpres': +d[0]['minpres'],
              'distance': +d[0]['distance']
          };
      })
      .map(csv);

  display('fixes');
});

function display(metric) {
  var formatValue = formatNumber,
       color = d3.scale.quantile();

  svg.each(function(year) {
    // TODO color range is calculated per year, should be over whole dataset
    color
        .domain(d3.values(data[year]).map(function(d) { return d[metric]; }))
        .range(d3.range(55, 255));

    d3.select(this).selectAll("rect.day")
      .attr("class", "day")
      .attr("style", function(d) {
          if (year in data && d in data[year]) {
                return 'fill:rgb(0,' + color(data[year][d][metric]) + ',0);';
          }
      })
      .select("title")
        .text(function(d) {
            if (year in data && d in data[year]) {
                return formatDate(d) + ": " + data[year][d][metric];
            } else {
                return formatDate(d) + ": NA";
            }
        });
  });
}

var lw = 200;
var lh = 20;
var legend = d3.select("#legend").append('svg')
  .attr('width', lw)
  .attr('height', lh + 30);

var gradient = legend.append("defs")
.append("linearGradient")
  .attr("id", "gradient")
  .attr("x1", "0%")
  .attr("y1", "0%")
  .attr("x2", "100%")
  .attr("y2", "0%")
  .attr("spreadMethod", "pad");

gradient.append("stop")
  .attr("offset", "0%")
  .attr("stop-color", 'rgb(0,55,0)')
  .attr("stop-opacity", 1);

gradient.append("stop")
  .attr("offset", "100%")
  .attr("stop-color", 'rgb(0,255,0)')
  .attr("stop-opacity", 1);

legend.append("rect")
  .attr("width", lw)
  .attr("height", lh)
  .style("fill", "url(#gradient)");

var g = legend.append('g');

g.append("text")
 .attr('x', 155)
 .attr('y', 40)
 .text('High');

g.append("text")
 .attr('x', 0)
 .attr('y', 40)
 .text('Low');

function monthPath(t0) {
  var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
      d0 = +day(t0), w0 = +week(t0),
      d1 = +day(t1), w1 = +week(t1);
  return "M" + (w0 + 1) * z + "," + d0 * z
      + "H" + w0 * z + "V" + 7 * z
      + "H" + w1 * z + "V" + (d1 + 1) * z
      + "H" + (w1 + 1) * z + "V" + 0
      + "H" + (w0 + 1) * z + "Z";
}

    </script>
  </body>
</html>
