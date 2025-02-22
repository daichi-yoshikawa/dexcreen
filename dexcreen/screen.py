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
