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


@dataclass(frozen=True)
class _Font:
  Size120: ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 120))
  Size80: ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 80))
  Size36: ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 36))
  Size24: ImageFont.FreeTypeFont = (
    ImageFont.truetype(os.path.join(PIC_PATH, FONT_FILE_NAME), 24))

Font = _Font()


