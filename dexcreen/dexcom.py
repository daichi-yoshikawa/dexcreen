import sys
import os
import math
import sqlite3
from datetime import datetime

from pydexcom import Dexcom as PyDexcom
from pydexcom.const import Region

from constants import DEXCOM


class Dexcom:
  def __init__(self):
    username = os.environ['DEXCOM_USERNAME']
    password = os.environ['DEXCOM_PASSWORD']
    region = os.environ['DEXCOM_REGION']
    unit = os.getenv('DEXCOM_READING_UNIT', 'mgdL')

    self.dexcom = PyDexcom(username=username, password=password, region=region)
    self.data = None

  def fetch(self):
    data = self.dexcom.get_current_glucose_reading()
    if data is None:
      return

    self.data = data

  @property
  def signal_loss(self):
    if self.data is None:
      return True

  @property
  def trend(self):
    return self.data.trend_description if self.data is not None else 'N/A'

  @property
  def arrow(self):
    return self.data.trend_arrow if self.data is not None else 'N/A'

  @property
  def mgdL(self):
    return self.data.value if self.data is not None else 'N/A'

  @property
  def mmoll(self):
    return self.data.mmol_l if self.data is not None else 'N/A'

  @property
  def timestamp(self):
    return self.data.datetime if self.data is not None else 'N/A'

  @property
  def diff_mins(self):
    if self.data is None:
      return None

    latest = datetime.fromisoformat(
      self.timestamp.strftime(DEXCOM.TIMESTAMP_FORMAT))
    now = datetime.now(latest.tzinfo)
    diff_mins = (now - latest).total_seconds() / 60
    return math.floor(diff_mins)

  @property
  def n_mins_ago(self):
    if self.data is None:
      return 'N/A'

    latest = datetime.fromisoformat(
      self.timestamp.strftime(DEXCOM.TIMESTAMP_FORMAT))
    now = datetime.now(latest.tzinfo)
    diff_mins = (now - latest).total_seconds() / 60
    diff_mins = math.floor(min(diff_mins, 60))

    if diff_mins == 0:
      return 'Now'
    return f'{diff_mins} min{"s" if diff_mins > 1 else ""} ago'
