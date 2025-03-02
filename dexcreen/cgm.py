import sys
import os
import math
import random
import re
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from pydexcom import Dexcom as PyDexcom
from pydexcom.const import Region, TREND_ARROWS, TREND_DESCRIPTIONS

from constants import DEXCOM


class Cgm(ABC):
  @abstractmethod
  def fetch(self):
    pass

  @property
  @abstractmethod
  def is_dummy(self):
    pass

  @property
  @abstractmethod
  def signal_loss(self):
    pass

  @property
  @abstractmethod
  def trend(self):
    pass

  @property
  @abstractmethod
  def arrow(self):
    pass

  @property
  @abstractmethod
  def mgdL(self):
    pass

  @property
  @abstractmethod
  def mmoll(self):
    pass

  @property
  @abstractmethod
  def timestamp(self):
    pass

  @property
  @abstractmethod
  def diff_mins(self):
    pass

  @property
  @abstractmethod
  def n_mins_ago(self):
    pass


class DummyCgm(Cgm):
  DUMMY_MGDL_VALUES = [40, 60, 90, 120, 180, 240, 400]

  def fetch(self):
    pass

  @property
  def is_dummy(self):
    return True

  @property
  def signal_loss(self):
    return False

  @property
  def trend(self):
    return random.choice(TREND_DESCRIPTIONS)

  @property
  def arrow(self):
    return random.choice(TREND_ARROWS)

  @property
  def mgdL(self):
    return random.choice(self.DUMMY_MGDL_VALUES)

  @property
  def mmoll(self):
    return round(self.mgdL / 18)

  @property
  def timestamp(self):
    return datetime.now() + timedelta(seconds=10)

  @property
  def diff_mins(self):
    return random.choice([0, 1, 2, 3, 4, 5, 30, 100])

  @property
  def n_mins_ago(self):
    return random.choice([
      'Now', '1 min ago', '2 mins ago', '3 mins ago',
      '4 mins ago', '5 mins ago', '30 mins ago', '60+ mins ago',
    ])


class Dexcom(Cgm):
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
  def is_dummy(self):
    return False

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


def get_instance():
  use_dummy_cgm = os.getenv('USE_DUMMY_CGM', 'False').lower() in ['1', 'true', 'yes']
  return DummyCgm() if use_dummy_cgm else Dexcom()
