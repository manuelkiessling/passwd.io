# Deploying passwd.io for production use on Ubuntu GNU/Linux 12.04 LTS systems

    cd /opt
    sudo git clone https://github.com/ManuelKiessling/passwd.io.git

    sudo ln -s /opt/passwd.io/deployment/sysctl.d/passwd.io.conf /etc/sysctl.d/40-passwd.io.conf
    sudo service procps restart

    sudo apt-get install nginx-extras python-dev python-pip libpq-dev postgresql

    sudo su - postgres
    psql template1
     CREATE USER passwdio WITH PASSWORD 'YOUR_DB_PASSWORD_HERE';
     CREATE DATABASE passwdio;
     GRANT ALL PRIVILEGES ON DATABASE passwdio TO passwdio;
     \q
     exit

    sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
    sudo ln -s /opt/passwd.io/deployment/nginx/nginx.conf /etc/nginx/nginx.conf
    sudo mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
    sudo ln -s /opt/passwd.io/deployment/nginx/sites-available/default /etc/nginx/sites-available/default
    sudo service nginx start

    sudo mv /etc/postgresql/9.1/main/postgresql.conf /etc/postgresql/9.1/main/postgresql.conf.bak
    sudo ln -s /opt/passwd.io/deployment/postgresql/postgresql.conf /etc/postgresql/9.1/main/postgresql.conf

    sudo pip install virtualenv
    sudo mkdir /opt/passwd.io-env
    sudo virtualenv --no-site-packages /opt/passwd.io-env
    sudo ln -s /opt/passwd.io /opt/passwd.io-env/app

    cd /opt/passwd.io-env
    . bin/activate

    cd app
    sudo pip install -r requirements.txt .
    sudo sed -i 's/ exceptions / exc /g' ../local/lib/python2.7/site-packages/migrate/versioning/schema.py

    sudo mkdir /var/run/passwd.io
    sudo mkdir /var/log/passwd.io
    sudo chown nobody:nogroup /var/run/passwd.io /var/log/passwd.io

There are two places where you need to change the database password from
*YOUR_DB_PASSWORD_HERE* to the database password you have chosen:
* /opt/passwd.io-env/app/production.ini, line 13
* /opt/passwd.io-env/app/migrations/manage.production.py, line 5

    sudo su - nobody
    bash
    cd /opt/passwd.io-env
    . bin/activate
    cd app
    python migrations/manage.production.py version_control
    python migrations/manage.production.py upgrade
    uwsgi --ini-paste-logged production.ini

You can reload the server with

    uwsgi --reload /var/run/passwd.io/uwsgi.pid

