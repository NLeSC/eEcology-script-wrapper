<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script - ${task.name}</title>
</head>
<body>
	<h1>${task.name}</h1>
	<div>
	${task.description}
	</div>
	<form method="POST">
		<label for="id">Tracker id</label> <input type="text" name="id">
		<label for="start">Start</label> <input type="datetime" name="start">
		<label for="end">End</label> <input type="datetime" name="end">
		<input type="submit"> <input type="reset">
	</form>
Form fields:
<pre>${task.formfields()}</pre>
</body>
</html>