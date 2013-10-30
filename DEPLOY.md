# Deploying passwd.io

The following recipe has been tested to work on Ubuntu 12.04 LTS systems.

The goal is to have the passwd.io backend running and to make the informational
homepage available at, e.g., https://www.example.com, and the actual web
application at https://example.com.

Accordingly, this recipe was used to set up https://www.passwd.io and
https://passwd.io.

The approach here is to set up the following stack:

- PostgreSQL, for storing the encrypted user data
- A Python 3 virtualenv that runs the application through uWSGI
- Nginx, for serving the static homepage directly, and the web application
  by using the uWSGI backend

In order to keep things reasonably secure, we will install all application files
with root as their owner, but run the application itself as user nobody.

As a prerequisite, you need a running Ubuntu 12.04 LTS GNU/Linux system to which
you have root (or at least, sudo) access to, and an SSL key/cert pair for your
domain stored at /etc/ssl/private/passwdio.key and /etc/ssl/certs/passwdio.crt,
respectively.

The recipe assumes that passwd.io is the only application/website you are going
to run on your system, therefore, it quite aggressively replaces central config
files, e.g. for Nginx and PostgreSQL.

We start by installing required Ubuntu packages:

    sudo apt-get install screen nginx-extras python3 python3-dev python-virtualenv libpq-dev postgresql

Now we can set up the database. Please choose a good password and write it down
for future use:

    sudo su - postgres
    psql template1
     CREATE USER passwdio WITH PASSWORD 'YOUR_DB_PASSWORD_HERE';
     CREATE DATABASE passwdio;
     GRANT ALL PRIVILEGES ON DATABASE passwdio TO passwdio;
     \q
     exit

Next, we create a place for the application to live in and clone it from Github:

    cd /opt
    sudo git clone https://github.com/manuelkiessling/passwd.io.git

Now we can start to replace the stock Nginx and PostgreSQL configuration with
the passwd.io specific settings from the cloned repository:

    sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
    sudo ln -s /opt/passwd.io/deployment/nginx/nginx.conf /etc/nginx/nginx.conf
    sudo mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
    sudo ln -s /opt/passwd.io/deployment/nginx/sites-available/default /etc/nginx/sites-available/default
    sudo service nginx start

    sudo mv /etc/postgresql/9.1/main/postgresql.conf /etc/postgresql/9.1/main/postgresql.conf.bak
    sudo ln -s /opt/passwd.io/deployment/postgresql/postgresql.conf /etc/postgresql/9.1/main/postgresql.conf

    sudo ln -s /opt/passwd.io/deployment/sysctl.d/passwd.io.conf /etc/sysctl.d/40-passwd.io.conf
    sudo service procps restart

We can now start to set up the Python 3 virtualenv for the passwd.io
application:

    sudo virtualenv -p /usr/bin/python3 /opt/passwd.io-env
    sudo ln -s /opt/passwd.io /opt/passwd.io-env/app

    cd /opt/passwd.io-env
    source bin/activate

    cd app
    python setup.py develop

    sudo mkdir /var/run/passwd.io
    sudo mkdir /var/log/passwd.io
    sudo chown nobody:nogroup /var/run/passwd.io /var/log/passwd.io

In order to allow the passwd.io application to use the PostgreSQL database we
created, we need to change the production.ini configuration file (located at
/opt/passwd.io-env/app/production.ini). The string "YOUR_DB_PASSWORD_HERE" on
line 13 and 39 must be replaced with the actual database password you have
set earlier.

Now we can switch to the user nobody in order to set up the initial database
structure and to start the uWSGI application server:

    sudo su - nobody
    bash
    screen
    cd /opt/passwd.io-env
    source bin/activate
    cd app
    alembic -c production.ini upgrade head
    /opt/passwd.io-env/bin/uwsgi --paste config:/opt/passwd.io/production.ini --socket :9000

Put the screen session in the background with CTRL-A CTRL-D.

You can reload the server with

    uwsgi --reload /var/run/passwd.io/uwsgi.pid

Your application can now be reached on the web. Please no
