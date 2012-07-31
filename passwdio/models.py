from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class File(Base):
    __tablename__ = 'files'
    id = Column(String(36), default='', nullable=False, primary_key=True)
    owner_hash = Column(String(40), unique=True)
    access_hash = Column(String(40))
    content = Column(Text)

