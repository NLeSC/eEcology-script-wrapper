<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script - ${task.label}</title>
<link rel="stylesheet"
        href="http://cdn.sencha.com/ext/beta/4.2.0.489/resources/css/ext-all.css" type="text/css"></link>
<link rel="stylesheet"
        href="http://cdn.sencha.com/ext/beta/4.2.0.489/examples/ux/css/ItemSelector.css" type="text/css"></link>
<link rel="stylesheet"
        href="${request.static_url('trackertask:static/style.css')}" type="text/css"></link>
<script type="text/javascript" src="http://cdn.sencha.com/ext/beta/4.2.0.489/ext-all-dev.js"></script>
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
</head>
<body>
	<h1>${task.label}</h1>
	<div>
	${task.description}
	</div>
	<div id="form"></div>
</body>
</html>