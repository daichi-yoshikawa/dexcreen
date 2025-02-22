from datetime import datetime

from sqlalchemy import (
  MetaData, Table, Column, Integer, Numeric, String, DateTime,
  ForeignKey, CheckConstraint, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, nullable=False, unique=True)
  created_at = Column(DateTime, server_default=func.now())
  updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MgdlReaging(Base):
  __tablename__ = 'mgdl_readings'

  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(ForeignKey('users.id'), nullable=False)
  value = Column(Integer, nullable=False)
  timestamp = Column(DateTime, nullable=False)

  __table_args = (
    CheckConstraint('value > 0 AND value <= 500'),
  )

class MmollReading(Base):
  __tablename__ = 'mmoll_readings'

  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(ForeignKey('users.id'), nullable=False)
  value = Column(Numeric(3, 1), nullable=False)
  timestamp = Column(DateTime, nullable=False)

  __table_args = (
    CheckConstraint('value > 0.0 AND value <= 99.9'),
  )
