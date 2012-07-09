from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.onwer_hash.alter(name='owner_hash')

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.owner_hash.alter(name='onwer_hash')

