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


class CgmReading(Base):
  __tablename__ = 'cgm_readings'

  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(ForeignKey('users.id'), nullable=False)
  value = Column(Integer, nullable=False)
  timestamp = Column(DateTime, nullable=False)

  __table_args = (
    CheckConstraint('value > 0 AND value <= 500'),
  )
