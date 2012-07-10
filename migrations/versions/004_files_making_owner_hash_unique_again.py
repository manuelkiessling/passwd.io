from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.owner_hash.alter(unique=True)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.owner_hash.alter(unique=False)
