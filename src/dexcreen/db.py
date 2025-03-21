import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from .constants import CONSTANTS
from .models import User, CgmReading


logger = logging.getLogger(__name__)

class BaseDatabase(ABC):
  @abstractmethod
  def get_user_id(self, username):
    pass

  @abstractmethod
  def insert_reading(
      self, user_id, value, timestamp, unique_timestamp=False):
    pass

  @abstractmethod
  def select_readings(
      self, user_id, timedelta_minutes_from, timedelta_minutes_to):
    pass

  @abstractmethod
  def select_recent_readings(self, user_id, hours):
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
      self, user_id, value, timestamp, unique_timestamp=False):
    pass

  def select_readings(
      self, user_id, timedelta_minutes_from, timedelta_minutes_to):
    return []

  def select_recent_readings(self, user_id, hours):
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
      self, user_id, value, timestamp, unique_timestamp=False):
    if unique_timestamp:
      found = self.session.query(
        exists().where(CgmReading.timestamp == timestamp)).scalar()
      if found:
        return

    timestamp_utc = timestamp.astimezone(timezone.utc)
    reading = CgmReading(user_id=user_id, value=value, timestamp=timestamp_utc)
    self.session.add(reading)
    self.session.commit()

  def select_readings(
      self, user_id, timedelta_mins_from, timedelta_mins_to):
    now_utc = datetime.now(timezone.utc)
    timestamp_from = now_utc - timedelta(minutes=timedelta_mins_from)
    timestamp_to = now_utc - timedelta(minutes=timedelta_mins_to)

    readings = (
      self.session.query(CgmReading)
        .filter(
          CgmReading.user_id == user_id,
          CgmReading.timestamp > timestamp_from,
          CgmReading.timestamp <= timestamp_to)
    )

    return [reading.value for reading in readings]

  def select_recent_readings(self, user_id, hours):
    cutoff = datetime.now() - timedelta(hours=hours)
    readings = self.session.query(CgmReading)\
      .filter(CgmReading.user_id == user_id, CgmReading.timestamp >= cutoff)\
      .order_by(CgmReading.timestamp.asc())\
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



