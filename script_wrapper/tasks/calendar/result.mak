## -- encoding: utf-8 -
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.3.9/d3.min.js" charset="utf-8"></script>
<style type="text/css">
text.title {
  font-size: 22px;
}

.day {
  fill: #fff;
  stroke: #000;
  stroke-opacity: .1;
}

path.month {
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

select {
  width: 240px;
}

</style>
<div id="legend"></div>
<div>
  <div>GPS-tracker: ${query['tracker_id']}, </div>
  <div>Time range: ${query['start'].strftime('%Y-%m-%d %H:%M:%S')} - ${query['end'].strftime('%Y-%m-%d %H:%M:%S')} (Timezone is <a href="http://en.wikipedia.org/wiki/Coordinated_Universal_Time">UTC</a>)</div>
  <div>Metric:
  <select>
    <option  value="fixes">Nr. of GPS measurements</option>
    <option  value="accels">Nr. of accelerometer measurements</option>
    <option  value="distance">2D distance travelled (km)</option>
    <option  value="maxalt">Maximum altitude (m)</option>
    <option  value="avgalt">Average altitude (m)</option>
    <option  value="minalt">Minimum altitude (m)</option>
    <option  value="maxtemp">Maximum temperature (&deg;C)</option>
    <option  value="avgtemp">Average temperature (&deg;C)</option>
    <option  value="mintemp">Minimum temperature (&deg;C)</option>
  </select></div>
  <div>Move mouse over day to see date and value.</div>
  <div id="years"></div>
  <div>Download raw data <a href="${files['result.csv']}">here</a></div>
</div>
<script type="text/javascript">
var m = [49, 20, 20, 19], // top right bottom left margin
    w = 1220 - m[1] - m[3], // width
    h = 200 - m[0] - m[2], // height
    z = 22; // cell size

var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    month = d3.time.format("%B"),
    percent = d3.format(".1%"),
    data,
    colors = {},
    formatDate = d3.time.format("%Y-%m-%d"),
    formatNumber = d3.format(",d"),
    formatPercent = d3.format("+.1%");

var year_range = d3.range(${query['start'].year}, ${query['end'].year}+1);

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
    .attr('class', 'title')
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

var monthFormat = d3.time.format('%b');

svg.selectAll("path.month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("svg:path")
    .attr("class", "month")
    .attr("d", monthPath)
;

svg.selectAll("text.month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
    .enter().append('text')
        .attr("class", "month")
        .attr("y", -5)
        .attr("x", monthOffset)
        .text(monthFormat)
;

d3.select("select").on("change", function() {
    display(this.value);
});

d3.csv('${files['result.csv']}', function(csv) {
  var metrics = [
    'fixes',
    'distance',
    'accels',
    'maxalt', 'avgalt', 'minalt',
    'maxtemp', 'avgtemp', 'mintemp',
  ];

  // Parse dates, numbers and handle NA's
  csv.forEach(function(d) {
      d.date = formatDate.parse(d.date);
      metrics.forEach(function(m) {
          if (d[m] === 'NA') {
              d[m] = null;
          } else {
              d[m] = +d[m];
          }
      });
  });

  // Make color scales
  var minc = 55;
  var maxc = 255;
  metrics.forEach(function(m) {
      colors[m] =  d3.scale.linear().domain(d3.extent(csv, function(d) { return d[m]; })).rangeRound([minc, maxc]);
  });

  // Group data per year
  data = d3.nest()
      .key(function(d) { return d.date.getFullYear(); })
      .key(function(d) { return d.date; })
      .rollup(function(d) {
          var r = {};
          metrics.forEach(function(m) {
              r[m] = d[0][m];
          });
          return r;
      })
      .map(csv);

  display('fixes');
});

function display(metric) {
  var formatValue = formatNumber,
       color;

  svg.each(function(year) {
    color = colors[metric];

    // TODO update legend with min and max domain

    d3.select(this).selectAll("rect.day")
      .attr("class", "day")
      .attr("style", function(d) {
          if (year in data && d in data[year]) {
              if (data[year][d][metric] === null) {
                return 'fill:lightgray;';
              } else {
                return 'fill:rgb(0,' + color(data[year][d][metric]) + ',0);';
              }
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

  d3.select('#legend').select('#low_label').text(color.domain()[0]);
  d3.select('#legend').select('#high_label').text(color.domain()[1]);
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
 .attr('id', 'high_label')
 .attr('x', 200)
 .attr('y', 40)
 .attr('text-anchor', 'end')
 .text('High');

g.append("text")
 .attr('id', 'low_label')
 .attr('x', 0)
 .attr('y', 40)
 .text('Low');

function monthOffset(t0) {
    var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
    d0 = +day(t0), w0 = +week(t0),
    d1 = +day(t1), w1 = +week(t1);
    return  (w0 + 1) * z;
}

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
