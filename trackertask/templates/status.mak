<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Script wrapper - Status</title>
% if success:
<meta http-equiv="refresh" content="0;url=${result}" />
% else:
<meta http-equiv="refresh" content="10" />
% endif
</head>
<body>Script is in '${state}' status. This page will reload every 10 seconds.
</body>
</html>