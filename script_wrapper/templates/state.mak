<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply', script=task.name)}">${task.label}</a> - State
</%block>

<%block name="header">
% if ready:
    % if success:
    <meta http-equiv="refresh" content="0;url=${result}" />
    % else:
    <meta http-equiv="refresh" content="0;url=${request.route_path('error', script=task.name, taskid=request.matchdict['taskid'])}" />
    % endif
% else:
<meta http-equiv="refresh" content="5" />
% endif
</%block>

Script is in '${state}' state. This page will reload every 5 seconds.

<div id="cancel"></div>
<script type="text/javascript">
Ext.create('Ext.button.Button', {
  text: 'Cancel',
  renderTo: 'cancel',
  handler: function() {
    Ext.Msg.confirm(
      'Cancel script',
      'Are you sure you want cancel job?',
      function(button) {
        if (button === 'yes') {
            Ext.Ajax.request({
              url: '${request.route_url('state.json', script=task.name, taskid=request.matchdict['taskid'])}',
              method: 'DELETE',
              success: function() {
                window.location = '${request.route_path('apply', script=task.name)}';
              }
            });
        }
      }
    );
  }
});
</script>
<!--
${repr(state)}
 -->