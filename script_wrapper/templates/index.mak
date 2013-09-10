<%inherit file="base.mak"/>

<%block name="title">
Home
</%block>

<h2>Available scripts</h2>
<ul>
	% for task in sorted(tasks.values(), key=lambda task: task.name):
	<li><a href="${request.route_path('apply',script=task.name)}">${task.label}</a>,
		${task.description}</li>
	% endfor
</ul>
