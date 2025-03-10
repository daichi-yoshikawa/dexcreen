import os
import logging
import time
from datetime import datetime, timedelta
from statistics import mean

from . import cgm, db, epd
from .canvas import Canvas
from .chart import CgmChart
from .logger_setup import configure_logger


logger = logging.getLogger(__name__)

class Dexcreen:
  db = None
  epd = None
  cgm = None
  unit = None
  user_id = None
  canvas = None
  initialized = False
  last_timestamp = None

  n_retry = 0

  CGM_REFRESH_INTERVAL = 60 * 5
  INTERVAL_MARGIN = 10
  RECOVERY_INTERVAL = 45 * 5
  MIN_INTERVAL = 10
  MAX_RETRY = 3
  DISPLAY_HOURS = 3
  UNIT_MINS = 15
  DISPLAYED_CGM_READING_MAX=300
  DISPLAYED_CGM_READING_MIN=40

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
      self.epd.clear()
      self.epd.sleep()

  def init_db(self):
    logger.info('Initialize db...')
    self.db = db.get_instance()
    logger.info('Initialized db.')

  def load_config(self):
    logger.info('Loading config...')
    username = os.environ['DEXCOM_USERNAME']
    self.unit = os.environ['DEXCOM_UNIT']

    logger.debug('Load user_id...')
    self.user_id = self.db.get_user_id(username=username)
    logger.debug(f'Loaded user_id: {self.user_id}')

  def init_cgm(self):
    self.cgm = cgm.get_instance()

  def init_epd(self):
    logger.info('Initialize epd...')
    self.epd = epd.get_instance()
    self.epd.init()
    self.epd.clear()
    logger.info('Initialized epd.')

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
    if self.cgm.signal_loss:
      logger.info('Signal loss')
      return
    logger.info(
      f'{self.cgm.reading} {self.unit}, {self.cgm.trend}, '
      f'{self.cgm.arrow}, {self.cgm.n_mins_ago}, {self.cgm.timestamp}')

    if self.last_timestamp == self.cgm.timestamp:
      logger.info(
        'Same timestamp data is fetched. '
        'Skip inserting data to database.')
      return

    self.db.insert_reading(
      user_id=self.user_id, value=self.cgm.reading,
      timestamp=self.cgm.timestamp, unique_timestamp=True)

  def display_letters(self):
    if not self.initialized:
      return
    self.epd.init_part()

    canvas = Canvas(epd=self.epd, vertical=False, background_color=255)
    self.write_letters(canvas)
    self.epd.display_partial(self.epd.getbuffer(canvas.image),
      0, 0, self.epd.width, round(self.epd.height * 0.45))

  def write_letters(self, canvas):
    reading = self.cgm.reading if self.unit == 'mg/dL' else round(self.cgm.reading / 18, 1)
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
      (620 if self.cgm.arrow is None else 660, 100),
      f'{self.cgm.arrow}',
      size=80 if self.cgm.arrow is None else 100)

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

  def get_chart_data(self):
    x_ticks = self.DISPLAY_HOURS * 60 // self.UNIT_MINS
    chart_data = []

    for i in range(x_ticks):
      timedelta_mins_from = self.UNIT_MINS * (i + 1)
      timedelta_mins_to = self.UNIT_MINS * i

      readings = self.db.select_readings(
        user_id=self.user_id,
        timedelta_mins_from=timedelta_mins_from,
        timedelta_mins_to=timedelta_mins_to,
      )
      if len(readings) == 0:
        continue

      mean_value = round(mean(readings))
      chart_data.append(
        dict(
          value=mean_value,
          timedelta_mins_from=timedelta_mins_from,
          timedelta_mins_to=timedelta_mins_to,
        )
      )
    return chart_data

  def display_chart(self):
    if not self.initialized:
      return
    self.epd.init_part()

    logger.info('display_chart')
    chart_data = self.get_chart_data()

    chart = CgmChart(
      epd=self.epd,
      x_offset=0,
      y_offset=round(self.epd.height*0.45),
      display_hours=self.DISPLAY_HOURS,
      unit_mins=self.UNIT_MINS,
      y_max=self.DISPLAYED_CGM_READING_MAX,
      y_min=self.DISPLAYED_CGM_READING_MIN,
      unit=self.unit,
      background_color=255)

    chart.draw(chart_data=chart_data)
    self.write_letters(chart.canvas)
    self.epd.display(self.epd.getbuffer(chart.canvas.image))
