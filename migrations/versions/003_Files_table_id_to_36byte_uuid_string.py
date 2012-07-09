from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.id.alter(type=String(36), default="", nullable=False)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    files.c.id.alter(type=Integer)
