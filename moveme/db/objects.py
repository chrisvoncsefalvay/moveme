# coding=utf-8

"""
objects is responsible for [brief description here].
"""

from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from moveme.utils.barcode_printer import BarcodePrinter
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


class Application(object):

    def __init__(self, printer_name, db_path="moveme.db"):
        Session = sessionmaker(bind=create_engine(db_path))
        self.sessh = Session()
        self.printer = BarcodePrinter(printer_name=printer_name)

    def create_box(self, *args, **kwargs):
        box = Box(*args, **kwargs)
        self.sessh.add(box)
        self.sessh.commit()

    def delete_box_by_uuid(self, box_uuid):
        self.sessh.query(Box).filter(Box.box_uuid == box_uuid).delete(synchronize_session='evaluate')

        affected_items = self.sessh.query(Item).filter(Item.in_box == box_uuid).all()
        for each in affected_items:
            each.in_box = ""
        self.sessh.commit()

    def alter_box_by_uuid(self, box_uuid, description=None, location=None):
        box = self.sessh.query(Box).filter(Box.box_uuid == box_uuid)
        description = description or box[0].description
        location = location or box[0].location
        box.update({"description": description, "location": location, "last_modified": make_timestamp()}, synchronize_session='evaluate')
        self.sessh.commit()

    def query_boxes(self):
        result = self.sessh.query(Box).filter().all()

        return [[box.box_uuid, box.description, box.location] for box in result]

    def query_boxids(self):
        result = self.sessh.query(Box).filter().all()

        return [box.box_uuid for box in result]

    def query_box_by_uuid(self, uuid):
        return self.sessh.query(Box).filter(Box.box_uuid == uuid).all()[0]


    def create_item(self, *args, **kwargs):
        item = Item(**kwargs)
        self.sessh.add(item)
        self.sessh.commit()

    def delete_item_by_uuid(self, item_uuid):
        self.sessh.query(Item).filter(Item.item_uuid == item_uuid).delete(synchronize_session='evaluate')
        self.sessh.commit()

    def alter_item_by_uuid(self, item_uuid, description=None, in_box=None):
        item = self.sessh.query(Item).filter(Item.item_uuid == item_uuid)
        description = description or item[0].description
        in_box = in_box or item[0].in_box
        item.update({"description": description, "in_box": in_box, "last_modified": make_timestamp()}, synchronize_session='evaluate')
        self.sessh.commit()

    def query_items(self, by_box=None):
        if by_box:
            result = self.sessh.query(Item).filter(Item.in_box == by_box).all()
        else:
            result = self.sessh.query(Item).filter().all()

        return [[item.item_uuid, item.description, item.box] for item in result]

    def query_item_by_uuid(self, uuid):
        return self.sessh.query(Item).filter(Item.item_uuid == uuid).all()[0]

    def label(self, item_uuid):
        self.printer.print_barcode(item_uuid)