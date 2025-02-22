import os
import datetime
import sqlite3

from dotenv import load_dotenv

from constants import DEXCOM


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
