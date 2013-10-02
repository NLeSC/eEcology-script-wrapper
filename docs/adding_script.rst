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

3. Define form
==============

Edit ``script_wrapper/tasks/<script_id>/form.js``.


4. Validate form and map form result to script arguments
========================================================

In ``script_wrapper/tasks/<script_id>/__init__.py`` the ``formfields2taskargs`` function has to be customized.
This function recieves the form submission result.

After validation and mapping the script can be executed.

5. Run script
=============

The ``run`` function in ``script_wrapper/tasks/<script_id>/__init__.py`` has to be customized.
See documentation for ``run`` function and other scripts for examples.

The script has to be added to the ``script_wrapper/tasks/<script_id>/`` folder and ``script`` field in ``__init__.py`` has to set to it's filename.

Any binaries that the script calls should also be in ``script_wrapper/tasks/<script_id>/`` folder.

6. Collect output files
=======================

The script will generate one or more output files.
The return value of the ``run`` functions ``script_wrapper/tasks/<script_id>/__init__.py`` is the list of output files which will be presented to the end-user.
