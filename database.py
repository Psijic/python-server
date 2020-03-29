#!/usr/bin/python3
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = 'mpg'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    path = Column(String(256), nullable=False)
    key = Column(String(32), nullable=True)
    kid = Column(String(32), nullable=True)

    @property
    def serialize(self):
        # Return object data in serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'key': self.key,
            'kid': self.kid,
        }


engine = create_engine('sqlite:///videos.db')
Base.metadata.create_all(engine)
