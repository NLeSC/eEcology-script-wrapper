<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply', script=task.name)}">${task.label}</a> - State
</%block>

<style type="text/css">
.state {
  font-size: 200%;
}
</style>
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.3.9/d3.min.js" charset="utf-8"></script>
<script type="text/javascript">
Ext.onReady(function() {
	var interval = 5000;
	var template = new Ext.Template('<div>Script is in <span class="state">{0}</span> state.</div>');
	template.compile();

	var status = Ext.create('Ext.Component', {
      xtype: 'component',
      tpl: template,
      data: ["${state|n}"],
      renderTo: 'status_cont',
    });

	var radius = 50;
	var stepSize = 0.2
	var arcGen = d3.svg.arc()
	    .innerRadius(radius*0.6)
	    .outerRadius(radius)
	    .startAngle(0)
	    .endAngle((2*Math.PI)*stepSize);

	var spinner = d3.select('#spinner_cont').append("svg")
	    .attr("width", 100)
	        .attr("height", 100)
	        .append('g')
	              .attr('transform', 'translate(50,50)')
	;

    spinner.append("circle")
        .attr("cx", 0)
        .attr("cy", 0)
        .attr("r", 50)
        .style("stroke", "lightgray")
        .style("fill", "none");

	var arc = spinner.append("path")
	    .datum([stepSize])
	    .style("fill", "#009ee0")
	    .attr("d", arcGen);

	function stepSpin() {
	    var cAngle = arcGen.endAngle()();
	    arcGen.startAngle(cAngle);
	    arcGen.endAngle(cAngle+(2*Math.PI)*stepSize);
	    arc.transition().duration(interval*0.8).ease('linear').attr('d', arcGen);
	}

	var progress = Ext.create('Ext.ProgressBar', {
	    border: true,
	    listeners: {
	        'update': function() {
	          if (!progress.isWaiting()) return;
	          Ext.Ajax.request({
	            url: '${request.route_path('state.json', script=task.name, taskid=request.matchdict['taskid'])}',
	            method: 'GET',
	            success: function(response) {
	              var result = Ext.JSON.decode(response.responseText);
	              if (result.ready) {
	                  window.location = '${request.route_path('result', script=task.name, taskid=request.matchdict['taskid'])}';
	              } else {
	                  status.update([result.state]);
	                  stepSpin();
	              }
	            },
	            failure: function(response) {
	                progress.reset();
	                Ext.Msg.alert('Failed to fetch job status', 'Reload page to try again');
	            }
	          });
	        }
	    }
	});
	progress.wait({interval: interval});

	var cancel = Ext.create('Ext.button.Button', {
	  text: 'Cancel',
	  renderTo: 'cancel',
	  handler: function() {
	    // job could complete and redirect while cancelling so stop polling
	    progress.reset();
	    Ext.Msg.confirm(
	      'Cancel script',
	      'Are you sure you want cancel script?',
	      function(button) {
	        if (button === 'yes') {
	            Ext.Ajax.request({
	              url: '${request.route_path('state.json', script=task.name, taskid=request.matchdict['taskid'])}',
	              method: 'DELETE',
	              success: function() {
	                  window.location = '${request.route_path('apply', script=task.name)}';
	              },
	              failure: function() {
	                Ext.Msg.alert('Failed to cancel job', 'Failed to cancel job');
	              }
	            });
	        } else {
	           // continue polling when job cancel was cancelled
	           progress.wait({interval: interval});
	        }
	      }
	    );
	  }
	});
});
</script>
<div id="status_cont"></div>
<div id="spinner_cont"></div>
<div id="progress"></div>
Progress state will be refreshed every 5 seconds.
<div id="cancel"></div>
