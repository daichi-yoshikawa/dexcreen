import os
import sqlite3

from dotenv import load_dotenv


class Database:
  def __init__(self):
    load_dotenv()
    self.conn = sqlite3.connect(os.environ['SQLITE_DB_NAME'])
    self.cur = conn.cursor()

  def get_user_id(self, username):
    self.cur.execute('SELECT id FROM users WHERE username = ?', (username,))
    row = self.cur.fetchone()

    if row is not None:
      user_id = row[0]
    else:
      self.cur.execute('INSERT INTO users (username) VALUES (?)', (username,))
      self.conn.commit()
      user_id = cur.lastrowid

    conn.close()
    return user_id

  def insert_reading(self, user_id, value, timestamp, unit='mgdL'):
    table = 'mgdl_readings' if unit == 'mgdL' else 'mmoll_readings'
    self.cur.execute(f"""
      INSERT INTO {table} (user_id, value, timestamp) VALUES (?, ?, ?)
    """, (user_id, value, timestamp))
    self.conn.commit()
    self.conn.close()
