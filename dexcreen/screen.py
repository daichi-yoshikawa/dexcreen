import os
import importlib

from dotenv import load_dotenv


load_dotenv()

class WaveshareEpd:
  screen_module = None

  @classmethod
  def import_screen_module(cls):
    screen_module = os.getenv('SCREEN_MODULE', 'epd7in5_V2')
    try:
      cls.screen_module = importlib.import_module(f'waveshare_epd.{screen_module}')
    except ModuleNotFoundError:
      raise ImportError(f'Could not import waveshare_epd.{screen_module}')

  @classmethod
  def get_instance(cls):
    if cls.screen_module is None:
      cls.import_screen_module()
    return cls.screen_module.EPD()

  @classmethod
  def module_exit(cls):
    if cls.screen_module is None:
      cls.import_screen_module()
    cls.screen_module.epdconfig.module_exit(cleanup=True)
    

    
