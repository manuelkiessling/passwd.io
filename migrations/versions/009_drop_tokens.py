from sqlalchemy import *
from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from migrate import *

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    token = Column(String(40), default='', nullable=False, primary_key=True)
    bound_to = Column(String(64), default='')
    verification_code = Column(String(6))
    activated = Column(Boolean())

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    tokens = Table('tokens', meta, autoload=True)
    tokens.drop(migrate_engine)

def downgrade(migrate_engine):
    Token.__table__.create(migrate_engine)

