<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('index')}">Script Wrapper</a>
- Home
</%block>

<h2>Available scripts</h2>
<ul>
	% for task in sorted(tasks.values(), key=lambda task: task.name):
	<li><a href="${request.route_path('apply',script=task.name)}">${task.label}</a>,
		${task.title|n}</li>
	% endfor
</ul>

<h2>Adding your own script</h2>

Your own script can be added to the script wrapper.

Adding your script requires 2 steps:
<ol>
<li>The script needs to adhere to the <a href="${request.static_url('script_wrapper:static/docs/script_requirements.html')}">requirements</a></li>
<li>Contact <a href="mailto:s.verhoeven@esciencecenter.nl">s.verhoeven@esciencecenter.nl</a> to wrap your script.
</li>
</ol>
