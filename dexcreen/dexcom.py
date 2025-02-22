import sys
import os
import math
from datetime import datetime

from dotenv import load_dotenv
from pydexcom import Dexcom as PyDexcom
from pydexcom.const import Region

from constants import DEXCOM


class Dexcom:
  def __init__(self):
    load_dotenv()
    account_id = os.environ['DEXCOM_ACCOUNT_ID']
    username = os.environ['DEXCOM_USERNAME']
    password = os.environ['DEXCOM_PASSWORD']
    region = os.environ['DEXCOM_REGION']

    self.dexcom = (
      PyDexcom(account_id=account_id, password=password, region=region)\
        if account_id else\
          PyDexcom(username=username, password=password, region=region))
    self.data = None

  def fetch(self):
    self.data = self.dexcom.get_current_glucose_reading()

  @property
  def trend(self):
    return self.data.trend_description if self.data is not None else 'N/A'

  @property
  def arrow(self):
    return self.data.trend_arrow if self.data is not None else 'N/A'

  @property
  def mg_dL(self):
    return self.data.value if self.data is not None else 'N/A'

  @property
  def mmol_l(self):
    return self.data.mmol_l if self.data is not None else 'N/A'

  @property
  def timestamp(self):
    return self.data.datetime if self.data is not None else 'N/A'

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




  # @classmethod
  # def get_minutes_since(cls):
  #   if cls.data is None:
  #     return None
  #
  #   data_timestamp = datetime.fromisoformat(data_timestamp_str)
  #   now = datetime.now(data_timestamp.tzinfo)
  #   diff_minutes = (now - data_timestamp).total_seconds() / 60
  #   return diff_minutes

  # def get_minutes_since_str(data_timestamp_str):
  #   diff_minutes = get_minutes_since(data_timestamp_str)
  #   diff_minutes = math.floor(min(diff_minutes, 60))
  #
  #   if diff_minutes == 0:
  #     return 'Now'
  #   return f'{diff_minutes} min{"s" if diff_minutes > 1 else ""} ago'
  #
  # def fetch(self):
  #   self.data = dexcom.get_current_glucose_reading()

