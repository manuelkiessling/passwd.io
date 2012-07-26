#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='postgresql://passwdio:Jnx725Frs09Hmc628Tfa42jM@127.0.0.1/passwdio', debug='False', repository='./migrations')
