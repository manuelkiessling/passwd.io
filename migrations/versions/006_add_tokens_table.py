from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from migrate import *

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    token = Column(String(40), default="", nullable=False, primary_key=True)
    verification_code = Column(String(6))
    activated = Column(Boolean())

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    Token.__table__.create(migrate_engine)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    Token.__table__.drop(migrate_engine)

