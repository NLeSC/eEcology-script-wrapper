<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply',script=task.name)}">${task.label}</a> - Results
</%block>

% if 'query' in result.result:
<!-- Query:
${result.result['query']}
-->
%endif

% if len(files)>0:
<h2>Output files</h2>
<ol>
% for filename in files:
<li><a target="_new" href="${request.route_path('result_file',script=task.name, taskid=result.id, filename=filename)}">${filename}</a>
% endfor
</ol>
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
