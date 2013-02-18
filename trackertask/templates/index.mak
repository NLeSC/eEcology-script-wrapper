<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script wrapper</title>
</head>
<body>
<h1>Scripts</h1>
<ul>
% for s in tasks.values():
<li><a href="${request.route_path('apply',script=s.name)}">${s.label}</a>, ${s.description}</li>
% endfor
</ul>
</body>
</html>