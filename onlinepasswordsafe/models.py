from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

class File(Base):
    __tablename__ = 'files'
    id = Column(String(36), default="", nullable=False, primary_key=True)
    owner_hash = Column(String(40), unique=True)
    access_hash = Column(String(40))
    content = Column(Text)
