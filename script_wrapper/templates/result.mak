<%inherit file="base.mak"/>

<%block name="title">
<a href="${request.route_path('apply',script=task.name)}">${task.label}</a> - Results
</%block>

% if len(files)>0:
<h2>Output files:</h2>
<ol>
% for filename, url in files.items():
<li><a target="_new" href="${url}">${filename}</a>
% endfor
</ol>
% endif

% if result.failed():
Not successfully completed.
Return code is ${result.result['return_code']}.
% elif result.state == 'REVOKED':
Cancelled.
% else:
Successfully completed.
% endif
