Home
----
List of available scripts with hyperlink to form of script

Script form
-----------

Script’s name, description, author etc.
Form to select date range and trackers.
Additional options for specific script. Can be per tracker (eg. Color, icon) or global (eg. format).

On submit
---------

1. Celery task is started
2. Poll task status
3. Redirect to script result page for multiple outputs or directly to single output

Script requirements
-------------------
-  Id, package name of script
-  Name (human readable name), description, author(s)
-  Form definition, every script has it own form and reuses tracker, start, end components.
-  Form validation, optional? validation can be done in script or before script submission
-  Task, (derived from R, Matlab, python etc. superclass) which:
  1.  maps form field to command line arguments
  2. Executes script
  3. Result with output files
-  Result page

Script types
------------

R, Matlab, Octave, python etc.

R options:
- .R file location

Matlab options:
- Matlab Compile Runtime location (global)
- shell script to run executable

Octave options:
- .m file location

