import os
import importlib
from abc import ABC, abstractmethod


use_dummy_epd = os.getenv('USE_DUMMY_EPD', 'False').lower() in ['1', 'true', 'yes']
epd_module = os.getenv('SCREEN_MODULE', 'epd7in5_V2')
epd_module = importlib.import_module(f'waveshare_epd.{epd_module}')
epdconfig = importlib.import_module(f'waveshare_epd.epdconfig')

class BaseEpd(ABC):
  @abstractmethod
  def init(self):
    pass

  @abstractmethod
  def init_part(self):
    pass

  @abstractmethod
  def clear(self):
    pass

  @abstractmethod
  def getbuffer(self, image):
    pass

  @abstractmethod
  def display(self, image_buffer):
    pass

  @abstractmethod
  def display_partial(self, image_buffer, x, y, width, height):
    pass

  @abstractmethod
  def sleep(self):
    pass


class DummyEpd(BaseEpd):
  def init(self):
    pass

  def init_part(self):
    pass

  def clear(self):
    pass

  def getbuffer(self, image):
    pass

  def display(self, image_buffer):
    pass

  def display_partial(self, image_buffer, x, y, width, height):
    pass

  def sleep(self):
    pass

  @property
  def height(self):
    return 320

  @property
  def width(self):
    return 480


class Epd(epd_module.EPD):
  def init_part(self):
    # Do not call epdconfig.module_init() to avoid OSError: Too many open files.
    self.reset()
    self.send_command(0X00) # PANNEL SETTING
    self.send_data(0x1F) #KW-3f KWR-2F BWROTP 0f BWOTP 1f

    self.send_command(0x04) # POWER ON
    epdconfig.delay_ms(100)
    self.ReadBusy()

    self.send_command(0xE0)
    self.send_data(0x02)
    self.send_command(0xE5)
    self.send_data(0x6E)

    return 0

  def clear(self):
    super().Clear()

  def display_partial(self, image_buffer, x, y, width, height):
    super().display_Partial(image_buffer, x, y, width, height)

"""
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

  @property
  def is_dummy(self):
    return True
"""

def get_instance():
  return DummyEpd() if use_dummy_epd else Epd()

"""
def get_instance():
  use_dummy_epd = os.getenv('USE_DUMMY_EPD', 'False').lower() in ['1', 'true', 'yes']
  if use_dummy_epd:
    return DummyEpd()

  try:
    screen_module = os.getenv('SCREEN_MODULE', 'epd7in5_V2')
    screen_module = importlib.import_module(f'waveshare_epd.{screen_module}')
    return screen_module.EPD()
  except ModuleNotFoundError:
    raise ImportError(f'Could not import waveshare_epd.{screen_module}')
"""
