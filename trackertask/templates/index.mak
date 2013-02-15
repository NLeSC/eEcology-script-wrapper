<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script wrapper</title>
</head>
<body>
<h1>Scripts</h1>
<ul>
% for s in scripts.values():
<li><a href="${request.route_path('apply',script=s.id)}">${s.name}</a>, ${s.description}</li>
% endfor
</ul>
</body>
</html>