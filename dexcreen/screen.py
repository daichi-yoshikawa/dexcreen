import os
import importlib

from dotenv import load_dotenv


class WaveshareEpd:
  @staticmethod
  def get_instance():
    load_dotenv()
    screen_module = os.getenv('SCREEN_MODULE', 'epd7in5_V2')

    try:
      pymodule = importlib.import_module(f'waveshare_epd.{screen_module}')
    except ModuleNotFoundError:
      raise ImportError(f'Could not import waveshare_epd.{screen_module}')

    return pymodule.EPD()

  def __init__(self):
    self.epd = WaveshareEpd.get_instance()

  def init(self, **kwargs):
    pass

  def clear(self, **kwargs):
    pass

  def display(self, **kwargs):
    pass

  def sleep(self, **kwargs):
    pass

  def stop(self, **kwargs):
    pass

  @property
  def height(self):
    pass

  @property
  def width(self):
    pass
