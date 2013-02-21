<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Results</title>
</head>
<body>
<h1>Output files:</h1>
<ol>
% for file in files:
<li><a href=${file['url']}>${file['name']}</a>
% endfor
</ol>
</body>
</html>