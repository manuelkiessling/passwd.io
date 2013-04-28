Clone this repository into
/opt/passwd.io
as root

    sudo ln -s /opt/passwd.io/deployment/sysctl.d/passwd.io.conf /etc/sysctl.d/40-passwd.io.conf
    service procps start

    sudo apt-get install libpq-dev postgresql

    sudo su - postgres
    psql template1
     CREATE USER passwdio WITH PASSWORD 'Jnx725Frs09Hmc628Tfa42jM';
     CREATE DATABASE passwdio;
     GRANT ALL PRIVILEGES ON DATABASE passwdio TO passwdio;
     \q
     exit

    sudo apt-get install nginx-extras
    sudo rm /etc/nginx/nginx.conf
    sudo ln -s /opt/passwd.io/deployment/nginx/nginx.conf /etc/nginx/nginx.conf
    sudo rm /etc/nginx/sites-available/default
    sudo ln -s /opt/passwd.io/deployment/nginx/sites-available/default /etc/nginx/sites-available/default
    sudo service nginx start

    rm /etc/postgresql/9.1/main/postgresql.conf
    ln -s /opt/passwd.io/deployment/postgresql/postgresql.conf /etc/postgresql/9.1/main/postgresql.conf

    sudo apt-get install python-dev python-pip
    sudo pip install virtualenv
    sudo mkdir /opt/passwd.io-env
    sudo virtualenv /opt/passwd.io-env
    sudo ln -s /opt/passwd.io /opt/passwd.io-env/app
    cd /opt/passwd.io-env
    sed -i 's/ exceptions / exc /g' local/lib/python2.7/site-packages/migrate/versioning/schema.py
    . bin/activate
    cd app
    sudo pip install -r requirements.txt .
    sudo mkdir /var/run/passwd.io
    sudo mkdir /var/log/passwd.io
    sudo chown nobody:nogroup /var/run/passwd.io /var/log/passwd.io
    sudo chown -R nobody:nogroup /opt/passwd.io
    sudo chown -R nobody:nogroup /opt/passwd.io-env
    sudo su - nobody
    bash
    cd /opt/passwd.io-env
    . bin/activate
    cd app
    python migrations/manage.production.py version_control
    python migrations/manage.production.py upgrade
    uwsgi --ini-paste-logged production.ini

reload with
    uwsgi --reload /var/run/passwd.io/uwsgi.pid
