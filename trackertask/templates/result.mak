<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Results</title>
</head>
<body>
<h1>Output files:</h1>
<ol>
% for filename, url in files.items():
<li><a href=${url}>${filename}</a>
% endfor
</ol>
</body>
</html>