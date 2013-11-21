<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply',script=task.name)}">${task.label}</a> - Results
</%block>

% if result_html is None:
% if len(files) > 0:
<h2>Output</h2>
<ol>
% for filename, url in files.iteritems():
<li><a target="_blank" href="${url}">${filename}</a>
% endfor
</ol>
% endif
% else:
${result_html|n}
% endif

% if result.failed():
Not successfully completed.
<div>
	% if 'return_code' in result.result:
	Return code is ${result.result['return_code']}.
	% else:
	Error: ${result.result}
	% endif
</div>
% elif result.state == 'REVOKED':
Cancelled.
% else:
Successfully completed.
% endif
