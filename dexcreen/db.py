import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants import DEXCOM
from models import User, MgdlReading, MmollReading


load_dotenv()

logger = logging.getLogger(__name__)

class Database(ABC):
  @staticmethod

  @abstractmethod
  def get_user_id(self, username):
    pass

  @abstractmethod
  def insert_reading(self, user_id, value, timestamp, unit='mg/dL'):
    pass

  @abstractmethod
  def select_recent_readings(self, user_id, hours, unit='mg/dL'):
    pass

  @abstractmethod
  def close(self):
    pass


class SqliteDB(Database):
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

  def insert_reading(self, user_id, value, timestamp, unit='mg/dL'):
    model = MgdlReading if unit == 'mg/dL' else MmollReading
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


def get_db_instance(db_type='sqlite'):
  if db_type == 'sqlite':
    return SqliteDB(db_name=os.getenv('SQLITE_DB_NAME', 'sqlite.db'))

"""
class Database:
  def __init__(self):
    load_dotenv()
    self.conn = sqlite3.connect(os.environ['SQLITE_DB_NAME'])
    self.cur = self.conn.cursor()

  def get_user_id(self, username):
    self.cur.execute('SELECT id FROM users WHERE username = ?', (username,))
    row = self.cur.fetchone()

    if row is not None:
      user_id = row[0]
    else:
      self.cur.execute('INSERT INTO users (username) VALUES (?)', (username,))
      self.conn.commit()
      user_id = self.cur.lastrowid

    return user_id

  def insert_reading(self, user_id, value, timestamp, unit='mgdL'):
    table = 'mgdl_readings' if unit == 'mgdL' else 'mmoll_readings'
    if unit == 'mgdL':
      self.cur.execute('''
        INSERT INTO mgdl_readings (user_id, value, timestamp) VALUES (?, ?, ?)
      ''', (user_id, value, timestamp))
    elif unit == 'mmoll':
      self.cur.execute('''
        INSERT INTO mmoll_readings (user_id, value, timestamp) VALUES (?, ?, ?)
      ''', (user_id, value, timestamp))
    self.conn.commit()

  def select_readings(self, user_id, hours, unit='mgdL'):
    table = 'mgdl_reading' if unit == 'mgdL' else 'mmoll_readings'
    self.cur.execute(f'''
      SELECT value, timestamp FROM {table}
      WHERE user_id = ? AND timestamp >= DATETIME('now', '-{hours} hours')
      ORDER BY timestamp ASC
    ''', (user_id,))
    rows = self.cur.fetchall()

    x = []
    y = []
    for value, timestamp in rows:
      dt = datetime.strptime(timestamp, DEXCOM.TIMESTAMP_FORMAT)
      x.append(dt.timestamp())
      y.append(value)

    return x, y

  def close(self):
    self.conn.close()
"""
