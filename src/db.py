import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from constants import CONSTANTS
from models import User, MgdlReading, MmollReading


logger = logging.getLogger(__name__)

class BaseDatabase(ABC):
  @abstractmethod
  def get_user_id(self, username):
    pass

  @abstractmethod
  def insert_reading(
      self, user_id, value, timestamp, unit='mg/dL', unique_timestamp=False):
    pass

  @abstractmethod
  def select_recent_readings(self, user_id, hours, unit='mg/dL'):
    pass

  @abstractmethod
  def close(self):
    pass

  @property
  @abstractmethod
  def is_dummy(self):
    pass


class DummyDb(BaseDatabase):
  def get_user_id(self, username):
    return 1

  def insert_reading(
      self, user_id, value, timestamp, unit='mg/dL', unique_timestamp=False):
    pass

  def select_recent_readings(self, user_id, hours, unit='mg/dL'):
    x = []
    y = []
    return x, y

  def close(self):
    pass

  @property
  def is_dummy(self):
    return True


class SqliteDb(BaseDatabase):
  def __init__(self, db_name):
    logger.info(f'Create sqlite db session({db_name})...')

    self.db_name = db_name
    engine = create_engine(f'sqlite:///{db_name}')
    Session = sessionmaker(bind=engine)
    self.session = Session()

    logger.info('Created sqlite db session({db_name}).')

  def get_user_id(self, username):
    user = self.session.query(User).filter_by(username=username).first()
    if user is None:
      logger.info(f'Create user({username})...')
      user = User(username=username)
      self.session.add(user)
      self.session.commit()
      logger.info(f'Created user({username}).')

    return user.id

  def insert_reading(
      self, user_id, value, timestamp, unit='mg/dL', unique_timestamp=False):
    model = MgdlReading if unit == 'mg/dL' else MmollReading

    if unique_timestamp:
      exists = self.session.query(
        exists().where(model.timestamp == timestamp)).scalar()
      if exists:
        return

    reading = model(user_id=user_id, value=value, timestamp=timestamp)
    self.session.add(reading)
    self.session.commit()

  def select_recent_readings(self, user_id, hours, unit='mg/dL'):
    model = MgdlReading if unit == 'mg/dL' else MmollReading

    cutoff = datetime.now() - timedelta(hours=hours)
    readings = self.session.query(model)\
      .filter(model.user_id == user_id, model.timestamp >= cutoff)\
      .order_by(model.timestamp.asc())\
      .all()

    x = []
    y = []
    for reading in readings:
      x.append(reading.timestamp.timestamp())
      y.append(float(reading.value))

    return x, y

  def close(self):
    logger.info(f'Close sqlite db session({self.db_name})...')
    self.session.close()
    logger.info(f'Closed sqlite db session({self.db_name}).')

  @property
  def is_dummy(self):
    return False


def get_instance():
  use_dummy_db = os.getenv('USE_DUMMY_DB', 'False').lower() in ['1', 'true', 'yes']
  if use_dummy_db:
    return DummyDb()

  db_name = os.getenv('SQLITE_DB_NAME', 'sqlite.db')
  return SqliteDb(db_name=db_name)



