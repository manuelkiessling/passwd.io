### Getting Started
(on Ubuntu 12.04 LTS)

    sudo apt-get install python-dev python-pip libpq-dev
    sudo pip install virtualenv
    cd ~
    virtualenv passwd.io-env
    cd passwd.io-env
    source bin/activate
    git clone https://github.com/ManuelKiessling/passwd.io.git
    cd passwd.io
    pip install -e ./
    python migrations/manage.development.py version_control
    python migrations/manage.development.py upgrade
    python setup.py test
    pserve development.ini --reload

Visit http://localhost:6543/static/webapp/

