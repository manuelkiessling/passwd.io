import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid-debugtoolbar',
    'waitress',
    'uwsgi',
    'psycopg2',
    'sqlalchemy',
    'zope.sqlalchemy',
    'alembic',
    'webtest',
    ]

setup(name='PasswdIO',
      version='0.2',
      description='PasswdIO',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Manuel Kiessling',
      author_email='manuel@kiessling.net',
      url='https://www.passwd.io',
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

