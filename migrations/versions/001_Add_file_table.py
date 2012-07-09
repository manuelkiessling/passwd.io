from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from migrate import *

Base = declarative_base()

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    onwer_hash = Column(String(40), unique=True)
    access_hash = Column(String(40))
    content = Column(Text)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    File.__table__.create(migrate_engine)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    File.__table__.drop(migrate_engine)

