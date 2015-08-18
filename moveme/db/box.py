# coding=utf-8



"""
box is responsible for [brief description here].
"""

from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

from moveme.utils.timestamp import make_timestamp

Base = declarative_base()

class Box(Base):
    __tablename__ = 'boxes'

    internal_id = Column(Integer, Sequence('box_internal_id_sequence'), primary_key=True)
    box_uuid = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    last_modified = Column(String, nullable=True)

    def __init__(self, description, box_uuid, location=None):
        self.box_uuid = box_uuid
        self.description = description
        if location:
            self.location = location
        self.last_modified = make_timestamp()

    def __repr__(self):
        return "<Box ID %s: %s (current location: %s)>" %(self.box_uuid, self.description, self.location)
