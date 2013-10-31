<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply', script=task.name)}">${task.label}</a> - State
</%block>

<style type="text/css">
.state {
  font-size: 200%;
}
</style>
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

	var progress = Ext.create('Ext.ProgressBar', {
	    width: '100%',
	    renderTo: 'progress',
	    border: true,
	    listeners: {
	        'update': function() {
	          if (!progress.isWaiting()) return;
	          Ext.Ajax.request({
	            url: '${request.route_url('state.json', script=task.name, taskid=request.matchdict['taskid'])}',
	            method: 'GET',
	            success: function(response) {
	              var result = Ext.JSON.decode(response.responseText);
	              if (result.is_complete) {
	                  window.location = '${request.route_url('result', script=task.name, taskid=request.matchdict['taskid'])}';
	              } else {
	                  Ext.getCmp('status_cont').update([result.state]);
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
	              url: '${request.route_url('state.json', script=task.name, taskid=request.matchdict['taskid'])}',
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
<div id="progress"></div>
Progress will be refreshed every 5 seconds.
<div id="cancel"></div>
