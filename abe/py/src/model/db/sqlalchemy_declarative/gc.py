# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class AbeAttribute(Base):
    __tablename__ = 'abe_attribute'

    id = Column(Integer, primary_key=True)
    value = Column(String(255))
    gc_id = Column(ForeignKey(u'abe_group_gc.id', ondelete=u'CASCADE'), nullable=False, index=True)

    gc = relationship(u'AbeGroupGc')
    gms = relationship(u'AbeGroupGm', secondary='attribute_to_gm')


class AbeGroupGc(Base):
    __tablename__ = 'abe_group_gc'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    pk = Column(Text)
    mk = Column(Text)
    dek = Column(String(255))
    date_dek_created = Column(DateTime)
    conversion_factor = Column(BigInteger)
    mqtt_topic = Column(String(333))
    abe_type = Column(String(255))
    abe_curve = Column(String(255))


class AbeGroupGm(Base):
    __tablename__ = 'abe_group_gm'

    id = Column(Integer, primary_key=True)
    gc_id = Column(ForeignKey(u'abe_group_gc.id', ondelete=u'CASCADE'), nullable=False, index=True)
    name = Column(String(255))
    mqtt_topic = Column(String(333))
    gm_key = Column(String(255), index=True)
    sk = Column(Text)
    dek = Column(String(255))
    sn_access_structure = Column(Text)
    sn_pk = Column(Integer)
    sn_abe_type = Column(String(255))
    sn_abe_curve = Column(String(255))

    gc = relationship(u'AbeGroupGc')


t_attribute_to_gm = Table(
    'attribute_to_gm', metadata,
    Column('attribute_id', ForeignKey(u'abe_attribute.id'), primary_key=True, nullable=False, index=True),
    Column('gm_id', ForeignKey(u'abe_group_gm.id'), primary_key=True, nullable=False, index=True)
)
