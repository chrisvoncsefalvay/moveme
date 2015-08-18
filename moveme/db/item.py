# coding=utf-8

"""
item is responsible for [brief description here].
"""

from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from moveme.utils.timestamp import make_timestamp

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'

    internal_id = Column(Integer, Sequence('item_internal_id_sequence'), primary_key=True)
    item_uuid = Column(String, nullable=False)
    description = Column(String, nullable=True)
    in_box = Column(String, ForeignKey('boxes.box_uuid'), nullable=True)
    last_modified = Column(String, nullable=True)

    box = relationship("Box", backref=backref('items', order_by=internal_id))

    def __init__(self, description, item_uuid, in_box = None):
        self.item_uuid = item_uuid
        self.description = description
        if in_box:
            self.in_box = in_box
        self.last_modified = make_timestamp()

    def __repr__(self):
        return "<Item ID %s: %s>" % (self.item_uuid, self.description)