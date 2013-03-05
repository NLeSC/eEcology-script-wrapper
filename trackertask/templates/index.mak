<%inherit file="base.mak"/>

<%block name="title">
Script wrapper
</%block>

<h2>Available scripts</h2>
<ul>
	% for s in tasks.values():
	<li><a href="${request.route_path('apply',script=s.name)}">${s.label}</a>,
		${s.description}</li>
	% endfor
</ul>
