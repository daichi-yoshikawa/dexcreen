import sys
import os
import logging
import time
import threading
import traceback

from dotenv import load_dotenv

from constants import CONSTANTS
from db import get_db_instance
from dexcom import Dexcom
from dexcreen import Dexcreen
from drawer import Canvas
from logger_setup import configure_logger
from screen import WaveshareEpd


load_dotenv()

configure_logger()
logger = logging.getLogger(__name__)


"""
def init_db():
  db = None

  try:
    db = get_db_instance(db_type=CONSTANTS.DB_TYPE)
  except Exception as e:
    logger.error(e)
    logger.error('Failed to initialize database.')
    if db is not None:
      db.close()
    logger.info('Shutdown app in init_db()...')
    exit()

  return db

def load_data(db):
  config = None
  readings = None

  try:
    logger.info('Loading config...')
    username = os.environ['DEXCOM_USERNAME']
    unit = os.environ['DEXCOM_UNIT']
    no_screen = os.environ['DEBUG_WITHOUT_SCREEN']

    logger.debug('Load user_id...')
    user_id = db.get_user_id(username=username)
    logger.debug(f'Loaded user_id: {user_id}')

    logger.debug('Load last 3 hours cgm reading...')
    x, y = db.select_recent_readings(user_id=user_id, hours=3, unit=unit)
    logger.debug(f'Loaded. x: {len(x)} points, y: {len(y)} points')

    config = dict(unit=unit, no_screen=no_screen)
    readings = dict(x=x, y=y)
  except Exception as e:
    logger.error(e)
    logger.error('Failed to initialize app.')
    if db is not None:
      db.close()
    logger.error('Shutdown app in init()...')
    exit()

  return config, user_id, readings


def init_epd(db, no_screen=False):
  epd = None

  def cleanup_and_exit():
    if db is not None:
      db.close()
    if epd is not None:
      epd.Clear()
      WaveshareEpd.module_exit()
    logger.error('Shutdown app in init_epd()...')
    exit()

  try:
    logger.info('Initialize epd...')
    # WaveshareEpd.dummy = no_screen
    epd = WaveshareEpd.get_instance()
    epd.init()
    logger.info('Initialized epd.')
  except IOError as e:
    logging.error(e)
    cleanup_and_exit()
  except KeyboardInterrupt:
    logging.error("ctrl + c:")
    cleanup_and_exit()
  except Exception as e:
    logger.error(e)
    cleanup_and_exit()
    exit()

  return epd

def worker():
  while True:
    logger.info('hogehoge')
    time.sleep(3)
"""
lock = threading.Lock()
dexcreen = Dexcreen()


# TODO: Instead of sleep long time,
# set smaller sleep and 
def fetch_cgm_data(stop_event):
  while not stop_event.is_set():
    with lock:
      try:
        dexcreen.fetch_cgm_data()
      except Exception:
        stop_event.set()
    woke_up_early = stop_event.wait(timeout=30)
    if woke_up_early:
      break

# Every 1 sec
def refresh_screen_letters(stop_event):
  while not stop_event.is_set():
    with lock:
      try:
        dexcreen.display_letters()
      except Exception:
        stop_event.set()
    woke_up_early = stop_event.wait(timeout=3)
    if woke_up_early:
      break

# Every 15 mins
def refresh_screen_chart(stop_event):
  while not stop_event.is_set():
    with lock:
      try:
        dexcreen.display_chart()
      except Exception:
        stop_event.set()
    woke_up_early = stop_event.wait(timeout=60 * 10)
    if woke_up_early:
      break


def worker():
  logger.info('worker is called.')
  dexcreen = Dexcreen()

  while True:
    try:
      dexcreen.run()
      dexcreen.sleep()
    except KeyboardInterrupt as e:
      logger.info('ctrl + c')
      dexcreen.cleanup()
      logger.info('Shutdown app in worker...')
      exit()
    except Exception as e:
      logger.error(e)
      dexcreen.cleanup()
      logger.info('Shutdown app in worker...')
      exit()



if __name__ == "__main__":
  logger.info('Starting app...')

  dexcreen.init()

  stop_event = threading.Event()
  threads = [
    threading.Thread(target=fetch_cgm_data, args=(stop_event,)),
    threading.Thread(target=refresh_screen_letters, args=(stop_event,)),
    threading.Thread(target=refresh_screen_chart, args=(stop_event,)),
  ]

  for thread in threads:
    thread.start()

  try:
    for thread in threads:
      thread.join()
  except KeyboardInterrupt:
    logger.info('KeyboardInterrupt detected.')
    stop_event.set()
    for thread in threads:
      thread.join()
    logger.info('All threads stopped due to KeyboardInterrupt.')
  except Exception as e:
    logger.error('Exception in one of the threads: {e}')
    stop_event.set()
    for thread in threads:
      thread.join()
    logger.error('All threads stopped due to Exception.')
  else:
    logger.info('All threads stopped without error.')

  """
  th_fetch_cgm_data.start()
  th_refresh_screen_letters.start()
  th_refresh_screen_chart.start()

  th_fetch_cgm_data.join()
  th_refresh_screen_letters.join()
  th_refresh_screen_chart.join()
  """
  """

  db = init_db()
  config, user_id, readings = load_data(db)
  epd = init_epd(db, no_screen=config['no_screen'])

  try:
    logging.info('Authenticating dexom credential...')
    dexcom = Dexcom()
    logging.info('Successfully authenticated.')

    while True:
      dexcom.fetch()
      logger.info(
        f'{dexcom.mgdL} {config["unit"]}, {dexcom.trend}, '
        f'{dexcom.arriow}, {dexcom.n_mins_ago}')
      logger.info(f'{dexcom.timestamp}, {type(dexcom.timestamp)}')

      from datetime import datetime, timedelta
      print('debug1', type(dexcom.timestamp), type(timedelta(minutes=5, seconds=5)))
      print('debug2', dexcom.timestamp)
      target_timestamp = dexcom.timestamp + timedelta(minutes=5, seconds=5)
      print('target', target_timestamp)
      now = datetime.now().astimezone(target_timestamp.tzinfo)
      print('now', now)
      print(target_timestamp, now)
      if target_timestamp > now:
        delta = (target_timestamp - now).total_seconds()
        logger.info(f'Waiting time in seconds: {delta}')

      epd.init_part()
      canvas = Canvas(epd, vertical=False, background_color=255)
      canvas.write((10, 0), f'{dexcom.mgdL}{config["unit"]}', size=120)
      canvas.write((560, 0), f'{dexcom.arrow}', size=120)
      canvas.write((10, 140), f'{dexcom.n_mins_ago}', size=80)

      db.insert_reading(
        user_id=user_id, value=dexcom.mgdL, timestamp=dexcom.timestamp, unit=config['unit'])

      epd.display(epd.getbuffer(canvas.image))
      epd.sleep()
      time.sleep(3)
  except IOError as e:
    logging.error(e)
  except KeyboardInterrupt:
    logging.error("ctrl + c:")
  except Exception as e:
    pass
  finally:
    if db is not None:
      db.close()
    if epd is not None:
      epd.Clear()
      WaveshareEpd.module_exit()
  """

  # epd = None
  # try:
  #   # username = os.environ['DEXCOM_USERNAME']
  #   #
  #   # logger.info('Initialize database...')
  #   # db = db.get_instance(db_type='sqlite')
  #   # user_id = db.get_user_id(username=username)
  #   #
  #   # logger.info('Select last 3 hours readings...')
  #   # x, y = db.select_recent_readings(user_id=user_id, unit='mgdL')
  #   # logger.info(f'{x}, {y}')
  # 
  #   WaveshareEpd.dummy = config['no_screen']
  #   epd = WaveshareEpd.get_instance()
  #   epd.init()
  #   epd.Clear()
  # 
  #   logging.info('Authenticating dexom credential...')
  #   dexcom = Dexcom()
  #   logging.info('Successfully authenticated.')
  # 
  #   while True:
  #     dexcom.fetch()
  #     logger.info(
  #       f'{dexcom.mgdL} mg/dL, {dexcom.trend}, '
  #       f'{dexcom.arrow}, {dexcom.n_mins_ago}')
  # 
  #     epd.init_part()
  #     canvas = Canvas(epd, vertical=False, background_color=255)
  #     canvas.write((10, 0), f'{dexcom.mgdL}mg/dL', size=120)
  #     canvas.write((560, 0), f'{dexcom.arrow}', size=120)
  #     canvas.write((10, 140), f'{dexcom.n_mins_ago}', size=80)
  # 
  #     """
  #     db.insert_reading(
  #       user_id=user_id, value=dexcom.mgdL, timestamp=dexcom.timestamp, unit='mgdL')
  #     """
  # 
  #     epd.display(epd.getbuffer(canvas.image))
  #     epd.sleep()
  #     time.sleep(3)
  # 
  #   # Drawing on the Horizontal image
  #   # logging.info("Drawing on the Horizontal image...")
  #   # epd.init_fast()
  #   # Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
  #   # draw = ImageDraw.Draw(Himage)
  #   """
  #   draw.line((20, 50, 70, 100), fill = 0)
  #   draw.line((70, 50, 20, 100), fill = 0)
  #   draw.rectangle((20, 50, 70, 100), outline = 0)
  #   draw.line((165, 50, 165, 100), fill = 0)
  #   draw.line((140, 75, 190, 75), fill = 0)
  #   draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
  #   draw.rectangle((80, 50, 130, 100), fill = 0)
  #   draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
  #   """
  #   """
  #   # partial update
  #   logging.info("5.show time")
  #   epd.init_part()
  #   # Himage = Image.new('1', (epd.width, epd.height), 0)
  #   # draw = ImageDraw.Draw(Himage)
  #   num = 0
  #   while (True):
  #     draw.rectangle((10, 120, 130, 170), fill = 255)
  #     draw.text((10, 120), time.strftime('%H:%M:%S'), font = font24, fill = 0)
  #     epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
  #     num = num + 1
  #     if(num == 10):
  #       break
  #   """
  # except IOError as e:
  #   logging.info(e)
  # except KeyboardInterrupt:
  #   logging.info("ctrl + c:")
  # finally:
  #   epd.init()
  #   epd.Clear()
  #   WaveshareEpd.module_exit()
  #   db.close()
  #   exit()
