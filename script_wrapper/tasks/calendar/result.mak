## -- encoding: utf-8 -
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.3.9/d3.js" charset="utf-8"></script>
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
  width: 350px;
}

</style>
<div id="legend">
<div id="slider"></div>
</div>

<div>
  <div>GPS-tracker: ${query['tracker_id']}, </div>
  <div>Time range: ${query['start'].strftime('%Y-%m-%d %H:%M:%S')} - ${query['end'].strftime('%Y-%m-%d %H:%M:%S')} (Timezone is <a href="http://en.wikipedia.org/wiki/Coordinated_Universal_Time">UTC</a>)</div>
  <div>Metric:
  <select>
    <option value="fixes">Nr. of GPS measurements</option>
    <option value="accels">Nr. of accelerometer measurements</option>
    <option value="distance">2D distance travelled (km)</option>
    <option value="maxalt">Maximum altitude (m)</option>
    <option value="avgalt">Average altitude (m)</option>
    <option value="minalt">Minimum altitude (m)</option>
    <option value="maxtemp">Maximum temperature (&deg;C)</option>
    <option value="avgtemp">Average temperature (&deg;C)</option>
    <option value="mintemp">Minimum temperature (&deg;C)</option>
    <option value="minvbat">Minimum voltage battery (V)</option>
    <option value="maxgpsinterval">Maximum interval between GPS measurements (hh:mm:ss)</option>
    <option value="mingpsinterval">Minimum interval between GPS measurements (hh:mm:ss)</option>
  </select></div>
  <div>Move mouse over day to see date and value.</div>
  <div id="years"></div>
  <div>Download raw data <a href="${files['result.csv']}">here</a></div>
<div>
Low color:
<div id="lcol" class="colorPicker">
    <svg height=200></svg>
  </div>
High color:
<div id="hcol" class="colorPicker">
    <svg height=200></svg>
  </div>
</div>
</div>
<style>
.slider {
  fill:hsla(0,0%,75%,1);
}

.slider:hover,
.slider.dragging {
  fill-opacity:0.5;
}

.tLine {
  stroke-width:1px;
  stroke:hsla(0,0%,10%,1);
}

.colorBarTitle,
.colorBarValue {
  fill:#c1c1c1;
}

</style>
<script type="text/javascript">
var cp = window.cp || {};
window.cp = cp;

cp.colorpicker = function() {

    var dispatch = d3.dispatch('cpupdate')

    var boxSize = 145,
        barWidth = 450,
        barHeight = 25;

    function colorPicker(selection) {
      selection.each(function(data) {

        var barScales = data.map(function(d,i) {
          return d3.scale.linear().domain([0,barWidth]).range(d.range);
        })

        var sliderScales = data.map(function(d,i) {
          return d3.scale.linear().domain(d.range).range([-7,barWidth-7]).clamp(true);
        })

        var wrap = d3.select(this).selectAll('g').data([data]);
        var wrapEnter = wrap.enter().append('g').attr('class','wrap').attr('transform','translate(10,10)');

        /*************************
        /  Current color box
        /************************/

        var colorBoxWrap = wrapEnter.append('g').attr('class','colorBox-wrap')

        var cbTransparencyLines = colorBoxWrap.selectAll('line').data(d3.range(7.5,boxSize,10))
        cbTransparencyLines.enter().append('line').attr('class','tLineX tLine')
        cbTransparencyLines.enter().append('line').attr('class','tLineY tLine')

          wrap.selectAll('.tLineX')
            .attr('x1', function(d) { return d })
            .attr('x2', function(d) { return d })
            .attr('y1', 0)
            .attr('y2', boxSize)

          wrap.selectAll('.tLineY')
            .attr('y1', function(d) { return d })
            .attr('y2', function(d) { return d })
            .attr('x1', 0)
            .attr('x2', boxSize)

        var colorBox = colorBoxWrap.append('rect').attr('class','colorBox')

        colorBox
            .attr('height',boxSize)
            .attr('width',boxSize)
            .style('fill', 'hsla(' + data.map(function(d,i) { return d.value + d.postfix; }).join(',') + ')')
            .attr('rx',6)
            .attr('ry',6)

        /*************************
        /  Color bar wrapper and colors
        /************************/

        var colorBarWrap = wrapEnter.append('g').attr('class','colorBar-wrap')
            .attr('transform',function(d,i) { return 'translate(' + boxSize + ',0)'; })

        var colorBar = colorBarWrap.selectAll('g.colorBar').data(function(d) { return d; });
        var colorBarEnter = colorBar.enter().append('g').attr('class','colorBar');

        colorBarEnter
            .attr('transform',function(d,i) { return 'translate(50,' + (i * 40) + ')'; })
            ;

        colorBarEnter.append('rect')
            .style('fill','hsla(0,0%,0%,0)')
            .attr('height',barHeight)
            .attr('width',barWidth)
            ;

        var colorBarTitle = colorBarEnter.append('text').attr('class','colorBarTitle');

        colorBarTitle
            .attr('dx',-25)
            .attr('dy',17.5)
            .style('text-anchor','middle')
            .text(function(d) { return d.key;})

        var colorBarValue = colorBarEnter.append('text').attr('class','colorBarValue');

        colorBarValue
            .attr('dx',barWidth + 25)
            .attr('dy',17.5)
            .style('text-anchor','start')

        var barTransparencyLinesX = colorBar.selectAll('line.barTLineX').data(d3.range(5,barWidth,10))
        var barTransparencyLinesEnterX = barTransparencyLinesX.enter().append('line').attr('class','barTLineX tLine')
        var barTransparencyLinesY = colorBar.selectAll('line.barTLineY').data(d3.range(7.5,barHeight,10))
        var barTransparencyLinesEnterY = barTransparencyLinesY.enter().append('line').attr('class','barTLineY tLine')

        barTransparencyLinesX
            .attr('x1', function(d) { return d; })
            .attr('x2', function(d) { return d; })
            .attr('y1', 0)
            .attr('y2', barHeight)

        barTransparencyLinesY
            .attr('x1', 0)
            .attr('x2', barWidth)
            .attr('y1', function(d) { return d; })
            .attr('y2', function(d) { return d; })

        var barGradient = colorBar.selectAll('line.barGradientLine').data(function(d) { return d3.range(-1,barWidth,2)});
        var barGradientEnter = barGradient.enter().append('line').attr('class','barGradientLine')

        barGradientEnter
            .style('stroke-width',3)
            .attr('y1', 0)
            .attr('y2', 25)
            .attr('x1',function(d,i) { return d })
            .attr('x2',function(d,i) { return d });

        update();

        /*************************
        /  Slider Rects
        /************************/

        colorBarEnter.append('rect')
                      .attr('class','slider')
                      .attr('width',14)
                      .attr('height',37)
                      .attr('y', -6)
                      .attr('x', function(d,i) { return sliderScales[i](d.value) })

        var sliders = colorBar.select('.slider')

        var sliderDrag = d3.behavior.drag();

        sliderDrag
          .origin(function(d,i) { return {x:d3.select(this).attr('x'),y:d3.select(this).attr('y')};})
          .on('dragstart', function(d,i) { d3.select(this).classed('dragging',true) })
          .on('drag', function(d,i) {
            var slider = d3.select(this);
            var invertX = sliderScales[i].invert(d3.event.x);
            slider.attr('x',sliderScales[i](invertX));

            data[i].value = invertX;

            update();

            colorBox
              .style('fill', 'hsla(' + data.map(function(d,i) { return d.value + d.postfix; }).join(',') + ')')
          })
          .on('dragend', function(d,i) {
            d3.select(this).classed('dragging', false)
          })

        sliderDrag.call(sliders);

        /*************************
        /  Repeated Functions
        /************************/

        function update() {
            barGradient
                .style('stroke',function(d,i,j) {
                    var hsla = ['0','100%','50%','1'];
                    hsla = hsla.map(function(f,k) {
                      var currentScale = barScales[k]
                      var postfix = data[k].postfix
                      return k == j ? currentScale(d) + postfix : (data[k].value + postfix) || hsla[k];
                    })
                    return 'hsla(' + hsla.join(',') + ')';
                  })

            colorBarValue.text(function(d) { return (d.key == 'a' ? Math.round(d.value * 100)/100 : Math.round(d.value)) + d.postfix;})

            dispatch.cpupdate(data);
        }

      });

      return colorPicker;
    }

    colorPicker.dispatch = dispatch;

    colorPicker.boxSize = function(_) {
      if (!arguments.length) return boxSize;
      boxSize = _;
      return chart;
    }

    colorPicker.barWidth = function(_) {
      if (!arguments.length) return barWidth;
      barWidth = _;
      return chart;
    }

    colorPicker.barHeight = function(_) {
      if (!arguments.length) return barHeight;
      barHeight = _;
      return chart;
    }

    return colorPicker;

}

cp.converters = cp.converters || {};

cp.converters.dataToHslaString = function(d) {
          var valueString = d.map(function(d) {
            return (d.key == 'a' ? Math.round(d.value * 100)/100 : Math.round(d.value)) + d.postfix;
          }).join(',')
          return 'hsla(' + valueString + ')'
        }

cp.colorSystems = cp.colorSystems || {};

cp.colorSystems.hsla = [
        {'key':'h', 'value':0, 'range':[0,359], 'postfix':''},
        {'key':'s', 'value':100, 'range':[0,100], 'postfix':'%'},
        {'key':'l', 'value':50, 'range':[0,100], 'postfix':'%'},
        {'key':'a', 'value':1, 'range':[0,1], 'postfix':''}
        ];
</script>
<script type="text/javascript">
Ext.onReady(function() {
    var m = [49, 20, 20, 19], // top right bottom left margin
    w = 1220 - m[1] - m[3], // width
    h = 200 - m[0] - m[2], // height
    z = 22; // cell size

//var highColor = 'rgb(0,55,0)';
//var lowColor = 'rgb(0,255,0)';

var highColor = '#FF0000';
var lowColor = '#00FF00';

var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    month = d3.time.format("%B"),
    percent = d3.format(".1%"),
    data,
    colors = {},
    formatDate = d3.time.format("%Y-%m-%d"),
    formatNumber = d3.format(",d"),
    formatPercent = d3.format("+.1%"),
    formatTime = d3.time.format.utc('%H:%M:%S'),
    selected_metric = 'fixes',
    metric_ranges = {};

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
    selected_metric = this.value;
    display(this.value);
});

d3.csv('${files['result.csv']}', function(csv) {
  var metrics = [
    'fixes',
    'distance',
    'accels',
    'maxalt', 'avgalt', 'minalt',
    'maxtemp', 'avgtemp', 'mintemp',
    'minvbat',
    'maxgpsinterval', 'mingpsinterval'
  ];

  // Parse dates, numbers and handle NA's
  csv.forEach(function(d) {
      d.date = formatDate.parse(d.date);
      metrics.forEach(function(m) {
          if (d[m] === 'NA') {
              d[m] = null;
          } else {
              if (m === 'maxgpsinterval' || m === 'mingpsinterval') {
                  // interval is in seconds, date require ms
                  d[m] = new Date(d[m]*1000);
              } else {
                  d[m] = +d[m];
              }
          }
      });
  });

  // Make color scales
  metrics.forEach(function(m) {
      metric_ranges[m] = d3.extent(csv, function(d) { return d[m]; })
      if (m === 'maxgpsinterval' || m === 'mingpsinterval') {
          colors[m] =  d3.time.scale().domain(metric_ranges[m]).interpolate(d3.interpolateRgb).range([lowColor, highColor]);
      } else {
          colors[m] =  d3.scale.linear().domain(metric_ranges[m]).interpolate(d3.interpolateRgb).range([lowColor, highColor]);
      }
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

function clipped_display(metric, clip_low, clip_high) {
    var color = colors[metric];
    color.domain([clip_low, clip_high]);

    function formatMetricValue(value) {
        if (value === null) {
            return 'NA';
        }
        if (metric === 'maxgpsinterval' || metric === 'mingpsinterval') {
            // Interval can be longer than one day, so prepend number of days
            if (value < (1000*60*60*24)) {
                return formatTime(value);
            } else {
                var day_part = formatTime(value);
                var days = Math.floor(value/(1000*60*60*24));
                return days + " days " + day_part;
            }
        }
        return value;
    }

    svg.each(function(year) {
      d3.select(this).selectAll("rect.day")
        .attr("class", "day")
        .attr("style", function(d) {
            if (year in data && d in data[year]) {
                if (data[year][d][metric] === null) {
                  return 'fill: lightgray;';
                } else {
                  return 'fill:' + color(data[year][d][metric]) + ';';
                }
            }
        })
        .select("title")
          .text(function(d) {
              if (year in data && d in data[year]) {
                  return formatDate(d) + ": " + formatMetricValue(data[year][d][metric]);
              } else {
                  return formatDate(d) + ": NA";
              }
          });
    });

    d3.select('#legend').select('#low_label').text(formatMetricValue(clip_low));
    d3.select('#legend').select('#high_label').text(formatMetricValue(clip_high));
}

function display(metric) {
  var color = colors[metric];
  slider.setMinValue(metric_ranges[metric][0]);
  slider.setMaxValue(metric_ranges[metric][1]);
  slider.setValue(0, color.domain()[0]);
  slider.setValue(1, color.domain()[1]);
  clipped_display(metric, color.domain()[0], color.domain()[1]);
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
  .attr("class", "low")
  .attr("offset", "0%")
  .attr("stop-color", lowColor)
  .attr("stop-opacity", 1);

gradient.append("stop")
  .attr("class", "high")
  .attr("offset", "100%")
  .attr("stop-color", highColor)
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

var slider;
slider = Ext.create('Ext.slider.Multi', {
    width: 200,
    values: [0, 100],
    //increment: 5,
    minValue: 0,
    maxValue: 100,
    decimalPrecision: 3,
    renderTo: 'slider',
    listeners: {
        change: function(comp) {
            var clip_low = slider.getValue(0);
            var clip_high = slider.getValue(1);
            if (selected_metric === 'maxgpsinterval' || selected_metric === 'mingpsinterval') {
                clip_low = new Date(clip_low);
                clip_high = new Date(clip_high);
            }
            clipped_display(selected_metric, clip_low, clip_high);
        }
    }
});

var hcopi = cp.colorpicker();
var lcopi = cp.colorpicker();
var lowColorHsl = d3.hsl(lowColor);

d3.select('#lcol svg')
.datum([
        {'key':'h', 'value':lowColorHsl.h, 'range':[0,359], 'postfix':''},
        {'key':'s', 'value':lowColorHsl.s * 100, 'range':[0,100], 'postfix':'%'},
        {'key':'l', 'value':lowColorHsl.l * 100, 'range':[0,100], 'postfix':'%'},
        {'key':'a', 'value':1, 'range':[0,1], 'postfix':''}
        ])
.call(lcopi)
;

var highColorHsl = d3.hsl(highColor);

d3.select('#hcol svg')
  .datum([
          {'key':'h', 'value':highColorHsl.h, 'range':[0,359], 'postfix':''},
          {'key':'s', 'value':highColorHsl.s *100, 'range':[0,100], 'postfix':'%'},
          {'key':'l', 'value':highColorHsl.l *100, 'range':[0,100], 'postfix':'%'},
          {'key':'a', 'value':1, 'range':[0,1], 'postfix':''}
          ])
  .call(hcopi)
  ;

lcopi.dispatch.on('cpupdate', function(d) {
    lowColor = d3.hsl(d[0]['value'], d[1]['value']/100.0, d[2]['value']/100.0).toString();
    console.log(d,lowColor);
    if (!(selected_metric in colors)) return ;
    var range = colors[selected_metric].range();
    range[0] = lowColor;
    colors[selected_metric].range(range);
    gradient.select('stop.low').attr("stop-color", lowColor);
    var clip_low = slider.getValue(0);
    var clip_high = slider.getValue(1);
    clipped_display(selected_metric, clip_low, clip_high);
});

hcopi.dispatch.on('cpupdate', function(d) {
    highColor = d3.hsl(d[0]['value'], d[1]['value']/100.0, d[2]['value']/100.).toString();
    console.log(d,highColor);
    if (!(selected_metric in colors)) return ;
    var range = colors[selected_metric].range();
    range[1] = highColor;
    colors[selected_metric].range(range);
    gradient.select('stop.high').attr("stop-color", highColor);
    var clip_low = slider.getValue(0);
    var clip_high = slider.getValue(1);
    clipped_display(selected_metric, clip_low, clip_high);
});

});

</script>
