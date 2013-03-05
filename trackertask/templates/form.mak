<%inherit file="base.mak"/>

<%block name="title">
Script wrapper &raquo; ${task.label}
</%block>

<%block name="header">
<script type="text/javascript">
Ext.Loader.setConfig({
    enabled: true,
  //  disableCaching: false, // uncomment to use firebug breakpoints
    paths: {
      'Ext.ux': 'http://cdn.sencha.com/ext/beta/4.2.0.489/examples/ux',
      'Esc': '${request.static_url('trackertask:static/esc')}'
    }
  });
</script>
<script type="text/javascript" src="${request.route_path('jsform',script=task.name)}"></script>
</%block>

<h2>${task.label}</h2>
<div id="description">
${task.description}
</div>
<div id="form"></div>
