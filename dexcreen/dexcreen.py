import sys
import os
import logging
import time

from dotenv import load_dotenv

from constants import DEXCOM
from db import Database
from dexcom import Dexcom
from drawer import Canvas
from logger_setup import configure_logger
from screen import WaveshareEpd


load_dotenv()

configure_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
  logger.info('Starting app...')

  try:
    interval = int(os.getenv('FETCH_DATA_INTERVAL_SECONDS', 300))
    username = os.environ['DEXCOM_USERNAME']

    logger.info('Initialize database...')
    db = Database()
    user_id = db.get_user_id(username=username)

    logger.info('Select last 3 hours readings...')
    x, y = db.select_recent_readings(user_id=user_id, unit='mgdL')
    logger.info(f'{x}, {y}')

    epd = WaveshareEpd.get_instance()
    epd.init()
    epd.Clear()

    logging.info('Authenticating dexom credential...')
    dexcom = Dexcom()
    logging.info('Successfully authenticated.')

    while True:
      dexcom.fetch()
      logger.info(
        f'{dexcom.mgdL} mg/dL, {dexcom.trend}, '
        f'{dexcom.arrow}, {dexcom.n_mins_ago}')

      epd.init_part()
      canvas = Canvas(epd, vertical=False, background_color=255)
      canvas.write((10, 0), f'{dexcom.mgdL}mg/dL', size=120)
      canvas.write((560, 0), f'{dexcom.arrow}', size=120)
      canvas.write((10, 140), f'{dexcom.n_min_ago}', size=80)

      db.insert_reading(
        user_id=user_id, value=dexcom.mgdL, timestamp=dexcom.timestamp, unit='mgdL')

      epd.display(epd.getbuffer(canvas.image))
      epd.sleep()
      time.sleep(3)

    # Drawing on the Horizontal image
    # logging.info("Drawing on the Horizontal image...")
    # epd.init_fast()
    # Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Himage)
    """
    draw.line((20, 50, 70, 100), fill = 0)
    draw.line((70, 50, 20, 100), fill = 0)
    draw.rectangle((20, 50, 70, 100), outline = 0)
    draw.line((165, 50, 165, 100), fill = 0)
    draw.line((140, 75, 190, 75), fill = 0)
    draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    draw.rectangle((80, 50, 130, 100), fill = 0)
    draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    """
    """
    # partial update
    logging.info("5.show time")
    epd.init_part()
    # Himage = Image.new('1', (epd.width, epd.height), 0)
    # draw = ImageDraw.Draw(Himage)
    num = 0
    while (True):
      draw.rectangle((10, 120, 130, 170), fill = 255)
      draw.text((10, 120), time.strftime('%H:%M:%S'), font = font24, fill = 0)
      epd.display_Partial(epd.getbuffer(Himage),0, 0, epd.width, epd.height)
      num = num + 1
      if(num == 10):
        break
    """
  except IOError as e:
    logging.info(e)
  except KeyboardInterrupt:
    logging.info("ctrl + c:")
  finally:
    epd.init()
    epd.Clear()
    WaveshareEpd.module_exit()
    db.close()
    exit()
