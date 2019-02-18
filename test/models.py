from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Random(Base):
    __tablename__ = 'random'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
