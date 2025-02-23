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
  INTERVAL_MARGIN = 5
  RECOVERY_INTERVAL = 45 * 5
  MIN_INTERVAL = 10
  MAX_RETRY = 3

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
      self.epd.Clear()
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
    if self.cgm.signal_loss:
      return self.RECOVERY_INTERVAL

    estimated_next_timestamp = (
      self.cgm.timestamp + timedelta(
        seconds=self.CGM_REFRESH_INTERVAL + self.INTERVAL_MARGIN))
    now = datetime.now().astimezone(estimated_next_timestamp.tzinfo)
    delta = (estimated_next_timestamp - now).total_seconds()

    fetched_too_early_or_too_late = delta < 0
    if fetched_too_early_or_too_late:
      logger.debug('Fetched too early or too late.')
      if self.n_retry < self.MAX_RETRY:
        self.n_retry = min(self.n_retry + 1, self.MAX_RETRY)
        return self.MIN_INTERVAL
      return self.RECOVERY_INTERVAL

    self.n_retry = 0
    return delta

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
    if self.cgm.signal_loss:
      return

    self.db.insert_reading(
      user_id=self.user_id, value=self.cgm_value,
      timestamp=self.cgm.timestamp, unit=self.unit)

  def display_letters(self):
    if not self.initialized:
      return
    self.epd.init_part()

    canvas = Canvas(self.epd, vertical=False, background_color=255)
    self.write_letters(canvas)
    self.epd.display(self.epd.getbuffer(canvas.image))
    self.epd.sleep()

  def write_letters(self, canvas):
    canvas.write((20, 0), f'{self.cgm_value}', size=140)
    canvas.write(
      (270 if self.unit == 'mg/dL' else 300, 70), f'{self.unit}', size=60)
    canvas.write(
      (520 if self.unit == 'mg/dL' else 550, 0), f'{self.cgm.arrow}', size=140)

    diff_mins = self.cgm.diff_mins
    if diff_mins is None:
      canvas.write((30, 140), 'N/A', size=80)
    elif diff_mins == 0:
      canvas.write((30, 140), 'Now', size=80)
    elif diff_mins > 60:
      canvas.write((30, 140), f'60+', size=80)
      canvas.write((170, 165), f'mins ago', size=48)
    elif diff_mins > 9:
      canvas.write((30, 140), f'{diff_mins}', size=80)
      canvas.write((130, 165), f'mins ago', size=48)
    else:
      canvas.write((30, 140), f'{diff_mins}', size=80)
      text = 'mins' if diff_mins > 1 else 'min ago'
      canvas.write((85, 165), text, size=48)

  def display_chart(self):
    if not self.initialized:
      return
    self.epd.init_part()

    canvas = Canvas(self.epd, vertical=True, background_color=255)
    self.write_letters(canvas)
    #canvas.rectangle((20, 50, 70, 100))

