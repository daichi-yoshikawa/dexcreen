import os
import logging
import time
from datetime import datetime, timedelta

import cgm
import db
import epd
from canvas import Canvas
from chart import CgmChart
from logger_setup import configure_logger


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
    logger.info('Clean up dexcreen...')
    self.initialized = False

    if self.db is not None:
      logger.info('Close database...')
      self.db.close()
    if self.epd is not None:
      logger.info('Clear screen...')
      #self.epd.init()
      self.epd.clear()
      self.epd.sleep()

  def init_db(self):
    try:
      logger.info('Initialize db...')
      self.db = db.get_instance()
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
      self.cgm = cgm.get_instance()
    except Exception as e:
      logger.error(e)
      self.cleanup()
      logger.error('Shutdown app in init cgm...')
      exit()

  def init_epd(self):
    try:
      logger.info('Initialize epd...')
      self.epd = epd.get_instance()
      self.epd.init()
      self.epd.clear()
      logger.info('Initialized epd.')
    except KeyboardInterrupt as e:
      logger.info('ctrl + c')
      self.cleanup()
      logger.info('Shutdown app in init_epd...')
    except Exception as e:
      logger.error(e)
      self.cleanup()
      logger.error('Shutdown app in init_epd...')

  def get_interval(self):
    if self.cgm.signal_loss or self.cgm.is_dummy:
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
      if self.n_retry < self.MAX_RETRY:
        return self.MIN_INTERVAL
      return self.CGM_REFRESH_INTERVAL
    else:
      self.n_retry = 0

    return min(max(delta, 0), self.CGM_REFRESH_INTERVAL)

  def fetch_cgm_data(self):
    if not self.initialized:
      return

    self.cgm.fetch()
    logger.info(
      f'{self.cgm.reading} {self.unit}, {self.cgm.trend}, '
      f'{self.cgm.arrow}, {self.cgm.n_mins_ago}')
    if self.cgm.signal_loss:
      return

    self.db.insert_reading(
      user_id=self.user_id, value=self.cgm.reading,
      timestamp=self.cgm.timestamp, unit=self.unit)

  def display_letters(self):
    if not self.initialized:
      return
    self.epd.init_part()

    canvas = Canvas(epd=self.epd, vertical=False, background_color=255)
    self.write_letters(canvas)
    self.epd.display_partial(self.epd.getbuffer(canvas.image),
      0, 0, self.epd.width, round(self.epd.height * 0.5))

  def write_letters(self, canvas):
    reading = self.cgm.reading
    if reading is None:
      canvas.write((20, 0), 'N/A', size=200)
    elif self.unit == 'mg/dL':
      offset = 0 if reading < 100 else 100
      canvas.write((20, 0), f'{reading}', size=200)
      canvas.write((260 + offset, 135), f'{self.unit}', size=48)
    else:
      offset = 0 if reading < 10 else 100
      canvas.write((20, 0), f'{reading}', size=200)
      canvas.write((320 + offset, 135), f'mmol/L', size=48)
    canvas.write(
      (620 if self.cgm.arrow is None else 660, 80),
      f'{self.cgm.arrow}',
      size=80 if self.cgm.arrow is None else 120)

    diff_mins = self.cgm.diff_mins
    if diff_mins is None:
      canvas.write((620, 25), 'N/A', size=80)
    elif diff_mins == 0:
      canvas.write((610, 25), 'Now', size=80)
    elif diff_mins > 60:
      canvas.write((505, 25), f'60+', size=100)
      canvas.write((680, 40), f'mins', size=36)
      canvas.write((680, 76), f'ago', size=36)
    elif diff_mins > 9:
      canvas.write((545, 20), f'{diff_mins}', size=100)
      canvas.write((680, 40), f'mins', size=36)
      canvas.write((680, 76), f'ago', size=36)
    elif diff_mins > 1:
      canvas.write((600, 20), f'{diff_mins}', size=100)
      canvas.write((680, 40), f'mins', size=36)
      canvas.write((680, 76), f'ago', size=36)
    elif diff_mins == 1:
      canvas.write((620, 20), f'{diff_mins}', size=100)
      canvas.write((695, 40), f'min', size=36)
      canvas.write((695, 76), f'ago', size=36)

  def display_chart(self):
    if not self.initialized:
      return
    self.epd.init_part()

    chart = CgmChart(
      epd=self.epd,
      height=round(self.epd.height * 0.5),
      width=self.epd.width,
      x_offset=0,
      y_offset=round(self.epd.height*0.5),
      display_hours=3,
      y_max=300,
      y_min=40,
      unit=self.unit,
      background_color=255)
    chart.draw()
    self.write_letters(chart.canvas)
    self.epd.display(self.epd.getbuffer(chart.canvas.image))
