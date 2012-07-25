from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    tokens = Table('tokens', meta, autoload=True)
    col = Column('bound_to', String(64), default='')
    col.create(tokens)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    tokens = Table('tokens', meta, autoload=True)
    tokens.c.bound_to.drop()

