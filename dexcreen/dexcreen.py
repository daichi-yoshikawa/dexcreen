import sys
import os
import logging
import time

from constants import DEXCOM
from dexcom import Dexcom
from drawer import PIC_PATH
from logger_setup import configure_logger
from screen import WaveshareEpd


configure_logger()
logger = logging.getLogger(__name__)

# PIC_DIR = os.path.join(
#   os.path.dirname(
#     os.path.dirname(os.path.realpath(__file__))),
#   os.environ['WAVESHARE_E_PAPER_PIC'])
# LIB_DIR = os.path.join(
#   os.path.dirname(
#     os.path.dirname(os.path.realpath(__file__))),
#   os.environ['WAVESHARE_E_PAPER_LIB'])
#
# if os.path.exists(libdir):
#     sys.path.append(libdir)

# from waveshare_epd import epd7in5_V2
from PIL import Image, ImageDraw, ImageFont


if __name__ == "__main__":
  logger.info('Starting app...')

  try:
    # epd = WaveshareEpd.get_instance()
    # epd = epd7in5_V2.EPD()

    logging.info('Authenticating dexom credential...')
    # dexcom = Dexcom()
    # logging.info('Successfully authenticated.')
    #
    # dexcom.fetch()
    # logger.info(
    #     f'{dexcom.mg_dL} mg/dL, {dexcom.trend}, '
    #     f'{dexcom.arrow}, {dexcom.n_mins_ago}')
    # epd.init()
    # epd.Clear()

    # font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    # font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    # font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    # font80 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 80)
    # font120 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 120)

    # Drawing on the Horizontal image
    logging.info("Drawing on the Horizontal image...")
    # epd.init_fast()
    # Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Himage)

    # draw.text((10, 0), f'{glucose.value}mg/dL', font = font120, fill = 0)
    # draw.text((560, 0), f'{glucose.trend_arrow}', font = font120, fill = 0)
    # draw.text((10, 140), f'{n_mins_ago}', font = font80, fill = 0)
    # draw.text((10, 240), f'{glucose.trend_description}', font = font80, fill = 0)
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
    # epd.display(epd.getbuffer(Himage))
    time.sleep(20)
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
    # # Drawing on the Vertical image
    # logging.info("2.Drawing on the Vertical image...")
    # epd.init()
    # Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Limage)
    # draw.text((2, 0), 'hello world', font = font18, fill = 0)
    # draw.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    # draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
    # draw.line((10, 90, 60, 140), fill = 0)
    # draw.line((60, 90, 10, 140), fill = 0)
    # draw.rectangle((10, 90, 60, 140), outline = 0)
    # draw.line((95, 90, 95, 140), fill = 0)
    # draw.line((70, 115, 120, 115), fill = 0)
    # draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
    # draw.rectangle((10, 150, 60, 200), fill = 0)
    # draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
    # epd.display(epd.getbuffer(Limage))
    # time.sleep(2)

    # logging.info("Clear...")
    # epd.init()
    # epd.Clear()
    #
    # logging.info("Goto Sleep...")
    # epd.sleep()
  except IOError as e:
    logging.info(e)
  except KeyboardInterrupt:
    logging.info("ctrl + c:")
    # epd7in5_V2.epdconfig.module_exit(cleanup=True)
    exit()
