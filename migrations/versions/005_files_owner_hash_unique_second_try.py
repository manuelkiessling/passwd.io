from migrate.changeset.constraint import UniqueConstraint

from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('files', meta, autoload=True)
    cons = UniqueConstraint('owner_hash', table=files)
    cons.create()

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    cons = UniqueConstraint('owner_hash', table=files)
    cons.drop()
