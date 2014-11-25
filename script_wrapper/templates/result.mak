<%inherit file="base.mak"/>

<%block name="title">
% if task.made_by_researcher:
<a href="${request.route_path('index')}">Script Wrapper</a>
-
% endif
<a href="${request.route_path('apply',script=task.name)}">${task.label}</a> - Results
</%block>

<%block name="header">
% if len(files) == 1:
<meta http-equiv="refresh" content="0;URL='${files.values()[0]}'"/>  
% endif
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
% if len(files) == 1:
<p>The output file will be downloaded automatically. Problems with the download? Please use the link above.</p>
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
