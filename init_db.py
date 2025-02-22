import os
import sqlite3

from dotenv import load_dotenv


def create_tables(db_path):
  conn = sqlite3.connect(db_path)
  cur = conn.cursor()

  cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL
    )
  """)

  cur.execute("""
    CREATE TABLE IF NOT EXISTS mgdl_readings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      value INTEGER NOT NULL,
      timestamp DATETIME NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  """)

  cur.execute("""
    CREATE TABLE IF NOT EXISTS mmoll_readings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      value REAL NOT NULL,
      timestamp DATETIME NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  """)

  conn.commit()
  conn.close()


if __name__ == '__main__':
  load_dotenv()
  create_tables(db_path=os.environ['SQLITE_DB_NAME'])
