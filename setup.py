from setuptools import setup, find_packages

requires = [
    'pyramid',
    'waitress',
    'pyramid_debugtoolbar',
    'sqlalchemy',
    'geoalchemy',  # required for PostGIS geometry column type
    'pyramid_celery',
    'celery',
    'redis',
    'rpy2',
    'oct2py',
    'scipy',  # required by oct2py
    'numpy',  # required by scipy
    'mock',
    'nose',
    'psycopg2',  # required to connect to e-ecology database
]

setup(name='trackertask',
      version='0.0',
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
      test_suite='trackertask',
      install_requires = requires,
      entry_points="""\
      [paste.app_factory]
      main = trackertask:main
      """,
      )