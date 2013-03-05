<%inherit file="base.mak"/>

<%block name="title">
State
</%block>

<%block name="header">
% if success:
<meta http-equiv="refresh" content="0;url=${result}" />
% else:
<meta http-equiv="refresh" content="5" />
% endif
</%block>

Script is in '${state}' state. This page will reload every 5 seconds.
