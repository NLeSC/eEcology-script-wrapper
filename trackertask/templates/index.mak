<%inherit file="base.mak"/>

<%block name="title">
Home
</%block>

<h2>Available scripts</h2>
<ul>
	% for task in tasks.values():
	<li><a href="${request.route_path('apply',script=task.name)}">${task.label}</a>,
		${task.description}</li>
	% endfor
</ul>
