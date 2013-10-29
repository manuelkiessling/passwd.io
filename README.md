# passwd.io

[![Build Status](https://travis-ci.org/manuelkiessling/passwd.io.png?branch=master)](https://travis-ci.org/manuelkiessling/passwd.io)

This is the code behind https://passwd.io, the ultra-simple yet secure online password store.

## Architecture and stack

**passwd.io** is a web-based client/server application with a Python HTTP backend and a JavaScript frontend.

For the frontend, the application stack is *jQuery Mobile* and the *Stanford Javascript Crypto Library*,
on the backend it's *Pyramid*, *Nginx* and *PostgreSQL*.

## Requirements

In order to setup and run the backend stack, you need a Unix-like system (e.g. Linux or Mac OS X),
Python 2.7, PostgreSQL & libpq, and pip. All other requirements will be pulled through pip.
For development mode, you will also need sqlite.

## Setting up the development environment

### On Ubuntu GNU/Linux 12.04 LTS
    sudo apt-get install python-dev python-pip libpq-dev sqlite3
    sudo pip install virtualenv
    cd ~
    virtualenv --no-site-packages passwd.io-env
    cd passwd.io-env
    source bin/activate
    git clone https://github.com/ManuelKiessling/passwd.io.git ./app
    cd app
    pip install -r requirements.txt .
    sed -i 's/ exceptions / exc /g' ../local/lib/python2.7/site-packages/migrate/versioning/schema.py
    python migrations/manage.development.py version_control
    python migrations/manage.development.py upgrade
    python setup.py test
    pserve development.ini --reload

You can now open the web application at http://localhost:6543/static/webapp/

## Setting up a production system

Please see [DEPLOY.md](https://github.com/ManuelKiessling/passwd.io/blob/master/DEPLOY.md)
