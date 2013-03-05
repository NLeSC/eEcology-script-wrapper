<%inherit file="base.mak"/>

<%block name="title">
Script wrapper &raquo; Results
</%block>

<h2>Output files:</h2>
<ol>
% for filename, url in files.items():
<li><a href=${url}>${filename}</a>
% endfor
</ol>
