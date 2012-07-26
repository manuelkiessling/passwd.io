from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.owner_hash.alter(type=String(64), default="", nullable=False)
    files.c.access_hash.alter(type=String(64), default="", nullable=False)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.owner_hash.alter(type=String(40), default="", nullable=False)
    files.c.access_hash.alter(type=String(40), default="", nullable=False)
