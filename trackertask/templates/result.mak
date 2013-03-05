<%inherit file="base.mak"/>

<%block name="title">
Results
</%block>

<h2>Output files:</h2>
<ol>
% for filename, url in files.items():
<li><a href=${url}>${filename}</a>
% endfor
</ol>
