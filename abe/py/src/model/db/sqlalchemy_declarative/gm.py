# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


t_abe_gc_to_attribute = Table(
    'abe_gc_to_attribute', metadata,
    Column('gc_id', ForeignKey(u'abe_group_gc.id'), primary_key=True, nullable=False, index=True),
    Column('attribute_id', ForeignKey(u'abe_attribute.id'), primary_key=True, nullable=False, index=True)
)


t_abe_gm_to_attribute = Table(
    'abe_gm_to_attribute', metadata,
    Column('attribute_id', ForeignKey(u'abe_attribute.id'), nullable=False, index=True),
    Column('gm_id', ForeignKey(u'abe_group_gm.id'), nullable=False, index=True)
)


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


class AbeAttribute(AbeGroupGc):
    __tablename__ = 'abe_attribute'

    id = Column(ForeignKey(u'abe_group_gc.id'), primary_key=True, index=True)
    value = Column(String(255))

    gcs = relationship(u'AbeGroupGc', secondary='abe_gc_to_attribute')
    gms = relationship(u'AbeGroupGm', secondary='abe_gm_to_attribute')


class AbeGroupGm(AbeAttribute):
    __tablename__ = 'abe_group_gm'

    id = Column(ForeignKey(u'abe_attribute.id'), primary_key=True, index=True)
    gc_id = Column(ForeignKey(u'abe_group_gc.id'), nullable=False, index=True)
    name = Column(String(255))
    gm_key = Column(Integer, unique=True)
    sk = Column(Text)

    gc = relationship(u'AbeGroupGc')
