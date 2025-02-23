import os
import logging
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv

from constants import CONSTANTS
from db import get_db_instance
from dexcom import Dexcom
from drawer import Canvas
from logger_setup import configure_logger
from screen import WaveshareEpd


load_dotenv()

configure_logger()
logger = logging.getLogger(__name__)

class Dexcreen:
  db = None
  epd = None
  cgm = None
  unit = None
  user_id = None
  readings = dict(x=[], y=[])
  canvas = None
  initialized = False

  n_retry = 0

  CGM_REFRESH_INTERVAL = 60 * 5
  MIN_INTERVAL = 5
  MAX_RETRY = 5

  def init(self):
    self.init_db()
    self.load_config()
    self.init_cgm()
    self.init_epd()
    self.initialized = True

  def cleanup(self):
    self.initialized = False

    if self.db is not None:
      self.db.close()
    if self.epd is not None:
      self.epd.Clear()
      WaveshareEpd.module_exit()

  def init_db(self):
    try:
      logger.info('Initialize db...')
      self.db = get_db_instance(db_type=CONSTANTS.DB_TYPE)
      logger.info('Initialized db.')
    except Exception as e:
      logger.error(e)
      self.cleanup()
      logger.error('Shutdown app in init_db...')
      exit()

  def load_config(self):
    try:
      logger.info('Loading config...')
      username = os.environ['DEXCOM_USERNAME']
      self.unit = os.environ['DEXCOM_UNIT']
      self.no_screen = os.environ['DEBUG_WITHOUT_SCREEN']

      logger.debug('Load user_id...')
      self.user_id = self.db.get_user_id(username=username)
      logger.debug(f'Loaded user_id: {self.user_id}')

      logger.debug('Load last 3 hours cgm reading...')
      x, y = self.db.select_recent_readings(user_id=self.user_id, hours=3, unit=self.unit)
      self.readings = dict(x=x, y=y)
      logger.debug(f'Loaded x: {len(x)} points, y: {len(y)} points.')
    except Exception as e:
      logger.error(e)
      self.cleanup()
      logger.error('Shutdown app in load_config...')
      exit()

  def init_cgm(self):
    try:
      self.cgm = Dexcom()
    except Exception as e:
      logger.error(e)
      self.cleanup()
      logger.error('Shutdown app in init cgm...')
      exit()

  def init_epd(self):
    try:
      logger.info('Initialize epd...')
      WaveshareEpd.dummy = False
      self.epd = WaveshareEpd.get_instance()
      self.epd.init()
      self.canvas = Canvas(self.epd, vertical=False, background_color=255)
      logger.info('Initialized epd.')
    except KeyboardInterrupt as e:
      logger.info('ctrl + c')
      self.cleanup()
      logger.info('Shutdown app in init_epd...')
      exit()
    except Exception as e:
      logger.error(e)
      self.cleanup()
      logger.error('Shutdown app in init_epd...')
      exit()      

  def get_interval(self):
    target_timestamp = (
      self.cgm.timestamp + timedelta(seconds=self.CGM_REFRESH_INTERVAL))
    now = datetime.now().astimezone(target_timestamp.tzinfo)
    delta = (target_timestamp - now).total_seconds()
    logger.info(f'Wait {delta}sec')

    require_retry = delta > self.CGM_REFRESH_INTERVAL
    if require_retry:
      self.n_retry = min(self.n_retry + 1, self.MAX_RETRY)
      return self.MIN_INTERVAL if self.n_retry < self.MAX_RETRY else self.CGM_REFRESH_INTERVAL
    else:
      self.n_retry = 0

    return min(max(delta, 0), self.CGM_REFRESH_INTERVAL)

  @property
  def cgm_value(self):
    return self.cgm.mgdL if self.unit == 'mg/dL' else self.cgm.mmoll

  def fetch_cgm_data(self):
    if not self.initialized:
      return

    self.cgm.fetch()
    logger.info(
      f'{self.cgm_value} {self.unit}, {self.cgm.trend}, '
      f'{self.cgm.arrow}, {self.cgm.n_mins_ago}')

    self.db.insert_reading(
      user_id=self.user_id, value=self.cgm_value, timestamp=self.cgm.timestamp, unit=self.unit)

  def display_letters(self):
    if not self.initialized:
      return
    self.epd.init_part()

    canvas = Canvas(self.epd, vertical=False, background_color=255)
    canvas.write((10, 0), f'{self.cgm_value}{self.unit}', size=120)
    canvas.write((560, 0), f'{self.cgm.arrow}', size=120)
    canvas.write((10, 140), f'{self.cgm.n_mins_ago}', size=80)
    self.epd.display(self.epd.getbuffer(canvas.image))
    self.epd.sleep()

  def display_chart(self):
    if not self.initialized:
      return
