<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply',script=task.name)}">${task.label}</a> - State
</%block>

<%block name="header">
% if success:
<meta http-equiv="refresh" content="0;url=${result}" />
% else:
<meta http-equiv="refresh" content="5" />
% endif
</%block>

Script is in '${state}' state. This page will reload every 5 seconds.
