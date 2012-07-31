import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'sqlalchemy-migrate',
    'psycopg2',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'uwsgi',
    'WebTest',
    'BeautifulSoup',
    ]

setup(name='PasswdIO',
      version='0.0',
      description='PasswdIO',
      long_description=README + '\n\n' +  CHANGES,
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
      test_suite='passwdio',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = passwdio:main
      [console_scripts]
      initialize_PasswdIO_db = passwdio.scripts.initializedb:main
      """,
      )

