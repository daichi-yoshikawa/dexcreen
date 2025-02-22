import sys
import os
import dataclases import dataclass

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


load_dotenv()

PIC_PATH = os.path.join(
  os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
  os.environ['WAVESHARE_E_PAPER_PIC_PATH'])
LIB_PATH = os.path.join(
  os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
  os.environ['WAVESHARE_E_PAPER_LIB_PATH'])
FONT_FILE_NAME = 'Font.ttc'

if os.path.exists(LIB_PATH):
  sys.path.append(LIB_PATH)


Fonts = dict(
  120=ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 120)),
  80=ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 80)),
  36=ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 36)),
  24=ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 24)),
)


class Canvas:
  def __init__(self, epd, vertical=False, background_color=255):
    size = (epd.height, epd.width) if vertical else (epd.width, epd.height)
    self.image = Image.new('1', size, background_color)
    self.draw = ImageDraw.Draw(image)

  def write(self, xy, text, size, color=0):
    self.draw.text(xy=xy, text=text, fill=color, font=Fonts[size])

  def line(self, xy, color=0, width=0):
    self.draw.line(xy=xy, fill=color, width=width)

  def rectangle(self, xy, color=0, fill=False):
    self.draw.rectangle(xy=xy, outline=color, fill=fill)

  def arc(self, xy, color=0, fill=False):
    self.draw.arc(xy=xy, outline=color, fill=fill)

  def chord(self, xy, start, end, color=0, fill=None)
    self.draw.chord(xy=xy, start=start, end=end, outline=color, fill=fill)
