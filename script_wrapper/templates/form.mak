<%inherit file="base.mak"/>

<%block name="title">
% if task.made_by_researcher:
<a href="${request.route_path('index')}">Script Wrapper</a>
-
% endif
${task.label}
</%block>

<%block name="header">
<script type="text/javascript">
Ext.Loader.setConfig({
    enabled: true,
  //  disableCaching: false, // uncomment to use firebug breakpoints
    paths: {
      'Ext.ux': '${request.static_path('script_wrapper:static/ext/examples/ux')}',
      'Esc': '${request.static_path('script_wrapper:static/esc')}'
    }
  });
</script>
<script type="text/javascript" src="${request.route_path('jsform',script=task.name)}"></script>
</%block>

<h2>${task.label}</h2>
<div id="description">
${task.description|n}
</div>
<div id="form"></div>
