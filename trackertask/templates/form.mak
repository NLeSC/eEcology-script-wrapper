<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script - ${task.label}</title>
<link rel="stylesheet"
        href="https://extjs.cachefly.net/ext-4.1.0-gpl/resources/css/ext-all.css" type="text/css"></link>
<script type="text/javascript" src="https://extjs.cachefly.net/ext-4.1.0-gpl/ext-all-dev.js"></script>
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