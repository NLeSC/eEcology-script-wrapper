===============
Adding a script
===============

Adding a script is performed by the script wrapper administrator. As several files need to be added to the script wrapper application.

Adding a script consists out of several steps.

.. contents:: Steps
    :local:

1. Compiling Matlab script
==========================

To make Matlab script run without requiring a Matlab license token, it has to be compiled.

1. Copy script and all it dependencies like libraries (eg. openearth, googleearth) to a machine with a Matlab Compiler (``mcc``).
2. Load Matlab environment with ``module load matlab``. (Optional)
3. Compile it with ``mcc -mv -R -nodisplay -I <library> <script>.m [<dependency>.m]``.
4. Copy generated ``<script>`` and ``run_<script>.sh`` files back to script wrapper server.
5. The generated run script can not handle arguments with spaces. Fix ``run_<script>.sh`` by removing the lines from ``args=`` to ``done`` and use ``"$@"`` instead of ``$args``.

Example compilations:

.. code-block:: bash

    # Matlab script which uses openearth postgresql library
    mcc -mv -R -nodisplay -I openearth/io/postgresql -I openearth \
    -I openearth/general -I openearth/general/io_fun dbq.m

    # Matlab script like above, but also uses googleearth library and a dependency dist.m
    mcc -mv -R -nodisplay -I openearth/io/postgresql -I openearth \
    -I openearth/general -I openearth/general/io_fun -I googleearth gpsvis.m dist.m

2. Make skeleton
================

Depending on the language make a copy of ``script_wrapper/tasks/example_<language>`` to ``script_wrapper/tasks/<script_id>``.

In ``script_wrapper/tasks/<script_id>/__init__.py``:

* Replace ``class example_<language>`` with ``class <script_id>``.
* Fill in the fields at the beginning of the class (name, description, etc.).
* Enable script by setting ``autoregister`` to ``True``.
* By default the Matlab scripts will be compiled with Matlab 2012a, if the script has been compiled with a different version set the matlab_version property and make sure the Matlab Compile Runtime is installed and configured in the *.ini file.

3. Define form
==============

Edit ``script_wrapper/tasks/<script_id>/form.js``.

4. Validate form and map form result to script arguments
========================================================

In ``script_wrapper/tasks/<script_id>/__init__.py`` the ``formfields2taskargs`` function has to be customized.
This function recieves the form submission result.

After validation and mapping the script can be executed.

Examples of validation:

* Prevent script from running when there is no data or too much data to work with.
* Give hints which date range to choose.

Make use of colander (http://docs.pylonsproject.org/projects/colander/en/latest/index.html) for validation.

The script arguments must be JSON serializable, so don't pass objects like DateTime.

5. Run script
=============

The ``run`` function in ``script_wrapper/tasks/<script_id>/__init__.py`` has to be customized.
See documentation for ``run`` function and other scripts for examples.

The script has to be added to the ``script_wrapper/tasks/<script_id>/`` folder and ``script`` field in ``__init__.py`` has to set to it's filename.

Any binaries that the script calls should also be in ``script_wrapper/tasks/<script_id>/`` folder.

6. Run script response
======================

The script will generate one or more output files. The will be listed on the result page.

The response is a dict with the following keys:

1. query, the query object used as input for the script
2. return_code, the posix return code of a executable started. Implemented when task is subclassed from SubProcessTask or MatlabTask class.

7. Custom result page
=====================

By default the result page will consist out of a list of output files and a message whether script completed successfully.

The list of output files can be replaced with an string with html.
1. Set `result_template` in task class to a Mako template file.
2. Construct template, the variables available inside the template are:

  * `task`, that is task object or self
  * `celery` result object
  * `query`, same a run script response['query']
  * `files`, dictionary of with filename as key and url as value.

8. Add unit tests
=================

When script contains a lot of Python code write unit tests for it.
