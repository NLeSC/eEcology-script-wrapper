from setuptools import setup, find_packages

requires = [
    'pyramid_mako',
    'pyramid',
    'waitress',
    'Paste',
    'pyramid_debugtoolbar',
    'psycopg2',  # eecology is Postresql
    'sqlalchemy==0.8.4',
    'geoalchemy',  # required for PostGIS geometry column type
    'pyramid_celery',
    'celery==3.0.25',
    'redis',
    'iso8601',
    'pytz',
    'rpy2',
    'singledispatch', # required by rpy2
    'oct2py',
    'scipy',  # required by oct2py
    'numpy',  # required by scipy
    'mock',
    'nose',  # to run tests
    'sphinx==1.2.3',
    'rst2pdf',  # to create PDF of documentation
    'sphinx_bootstrap_theme',  # to create nice looking html documentation
    'simplekml',  # for pykml task
    'python_dateutil',  # requirement for gpxdata
    'gpxdata', # for gpx task
    'gunicorn',  # production wsgi server
    'colander',
]

exec(open('script_wrapper/version.py').read())

setup(name='script_wrapper',
      version=__version__,
      description='Run Matlab, R scripts via web front-end',
      long_description="",
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='script_wrapper',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = script_wrapper:main
      """,
      )
