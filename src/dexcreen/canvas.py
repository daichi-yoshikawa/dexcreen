import sys
import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont


PIC_PATH = os.path.join(
  os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
  os.environ['WAVESHARE_E_PAPER_PIC_PATH'])
LIB_PATH = os.path.join(
  os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
  os.environ['WAVESHARE_E_PAPER_LIB_PATH'])
FONT_FILE_NAME = 'Font.ttc'

if os.path.exists(LIB_PATH):
  sys.path.append(LIB_PATH)

Fonts = {
  '200': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 200),
  '140': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 140),
  '120': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 120),
  '100': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 100),
  '80': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 80),
  '60': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 60),
  '48': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 48),
  '36': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 36),
  '24': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 24),
  '18': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 18),
  '12': ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 12),
}

class Canvas:
  def __init__(self, epd, vertical=False, background_color=255):
    size = (epd.height, epd.width) if vertical else (epd.width, epd.height)
    self.image = Image.new('1', size, background_color)
    self.draw = ImageDraw.Draw(self.image)

  def write(self, xy, text, size, color=0):
    self.draw.text(xy=xy, text=text, fill=color, font=Fonts[f'{size}'])

  def line(self, xy, fill=0, width=0):
    self.draw.line(xy=xy, fill=fill, width=width)

  def rectangle(self, xy, outline=0, fill=None):
    self.draw.rectangle(xy=xy, outline=outline, fill=fill)

  def arc(self, xy, outline=0, fill=None):
    self.draw.arc(xy=xy, outline=outline, fill=fill)

  def chord(self, xy, start, end, outline=0, fill=None):
    self.draw.chord(xy=xy, start=start, end=end, outline=outline, fill=fill)
