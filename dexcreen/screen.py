import os
import importlib

from dotenv import load_dotenv


load_dotenv()


class DummyEpd:
  def init(self):
    pass

  def init_fast(self):
    pass

  def init_part(self):
    pass

  def Clear(self):
    pass

  @property
  def height(self):
    return 320

  @property
  def width(self):
    return 480

  def getbuffer(self, image):
    pass

  def display(self, image_buffer):
    pass

  def display_Partial(image_buffer, x, y, width, height):
    pass

  def sleep(self):
    pass


class WaveshareEpd:
  screen_module = None
  dummy = False

  @classmethod
  def import_screen_module(cls):
    screen_module = os.getenv('SCREEN_MODULE', 'epd7in5_V2')
    try:
      cls.screen_module = importlib.import_module(f'waveshare_epd.{screen_module}')
    except ModuleNotFoundError:
      raise ImportError(f'Could not import waveshare_epd.{screen_module}')

  @classmethod
  def get_instance(cls):
    if cls.dummy:
      return DummyEpd()

    if cls.screen_module is None:
      cls.import_screen_module()
    return cls.screen_module.EPD()

  @classmethod
  def module_exit(cls):
    if cls.dummy:
      return

    if cls.screen_module is None:
      cls.import_screen_module()
    cls.screen_module.epdconfig.module_exit(cleanup=True)
