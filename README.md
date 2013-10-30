# passwd.io

[![Build Status](https://travis-ci.org/manuelkiessling/passwd.io.png?branch=master)](https://travis-ci.org/manuelkiessling/passwd.io)

This is the code behind https://passwd.io, the ultra-simple yet secure online
password store.

## Architecture and stack

**passwd.io** is a web-based client/server application with a Python HTTP
backend and a JavaScript frontend.

For the frontend, the application stack is *jQuery Mobile* and the
*Stanford Javascript Crypto Library*, on the backend it's *Pyramid*, *Nginx* and
*PostgreSQL*.

## Requirements

In order to setup and run the backend stack, you need a Unix-like system (e.g.
Linux or Mac OS X), Python 3 (including the python3-dev package), PostgreSQL &
libpq-env, virtualenv, and git. All other requirements will be pulled through
setuptools. For development mode, you will also need sqlite3.

## Setting up the development environment

### On Debian 7 "Wheezy"
    sudo apt-get install python3-dev python3-pip libpq-dev sqlite3
    sudo pip-3.2 install virtualenv
    cd ~
    virtualenv-3.2 --no-site-packages passwd.io-env
    cd passwd.io-env
    source bin/activate
    git clone https://github.com/manuelkiessling/passwd.io.git ./app
    cd app
    python setup.py develop
    alembic -c development.ini upgrade head
    python setup.py test
    pserve development.ini --reload

You can now open the web application at http://localhost:6543/static/webapp/

## Setting up a production system

Please see
[DEPLOY.md](https://github.com/ManuelKiessling/passwd.io/blob/master/DEPLOY.md)
