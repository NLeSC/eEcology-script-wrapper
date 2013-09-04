===================
Script requirements
===================

Requirements where the script that is added needs to adhere to.

General
=======

Several pieces of information about the script are required:

* Id, identifier of the script, will be used in package and url.
* Name, Human readable name.
* Description, short description of script.
* What arguments are required to start script. Includes order, format, possible choices, db credentials and connection string.

Database
========

The script will be executed with the priveleges of the end-user. This means only use table/views everyone can use eg. only use *_limited views.

Matlab
======

Script will be run inside a directory so any generated output file should have no directory prefixed to it.
