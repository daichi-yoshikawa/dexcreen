from PIL import Image, ImageDraw

from .canvas import Canvas


class CgmChart:
  UNIT_MINS = 15

  def __init__(
      self, epd, x_offset=0, y_offset=0, display_hours=3,
      y_max=300, y_min=40, unit='mg/dL', background_color=255):
    self.padding_right = 40
    self.padding_bottom = 20

    self.height = epd.height - y_offset - self.padding_bottom
    self.width = epd.width - x_offset - self.padding_right

    self.canvas = Canvas(
      epd=epd, vertical=False, background_color=background_color)

    self.x_offset = x_offset
    self.y_offset = y_offset

    self.display_hours = display_hours

    self.y_max = y_max
    self.y_min = y_min

    self.unit = unit
    self.background_color = background_color

    self.font_size = 18
    self.block_height = 10

  @property
  def x_left(self):
    return self.x_offset

  @property
  def x_right(self):
    return self.x_left + self.width

  @property
  def y_top(self):
    return self.y_offset

  @property
  def y_bottom(self):
    return self.y_offset + self.height

  @property
  def xy_topleft(self):
    return (self.x_left, self.y_top)

  @property
  def xy_topright(self):
    return (self.x_right, self.y_top)

  @property
  def xy_bottomleft(self):
    return (self.x_left, self.y_bottom)

  @property
  def xy_bottomright(self):
    return (self.x_right, self.y_bottom)

  @property
  def pixels_per_x_unit(self):
    return self.width / self.display_hours / 60

  @property
  def pixels_per_y_unit(self):
    return self.height / (self.y_max - self.y_min)

  @property
  def x_of_y_scale(self):
    return self.x_right + 8

  @property
  def y_of_x_scale(self):
    return self.y_bottom

  def get_y_by_value(self, value):
    y_diff = max(self.y_max - value, 0)
    return self.y_top + round(self.pixels_per_y_unit * y_diff)

  def get_x_by_value(self, diff_mins):
    return self.x_right - round(self.pixels_per_x_unit * diff_mins)

  def draw_y_scale(self, value, disable_offset=False):
    y = self.get_y_by_value(value) - round(self.font_size * 0.5)
    self.canvas.write(
      (self.x_of_y_scale, y), f'{value}', self.font_size)

  def draw_x_scale(self, diff_mins, offset):
    x = self.get_x_by_value(diff_mins) - offset
    self.canvas.write(
      (x, self.y_of_x_scale), f'{diff_mins} mins ago', self.font_size)

  def draw_block(self, diff_mins_min, diff_mins_max, value):
    y = self.get_y_by_value(value)
    y_top = max(self.y_top, y - round(self.block_height * 0.5))
    y_bottom = min(self.y_bottom, y + round(self.block_height * 0.5))
    x_left = self.get_x_by_value(diff_mins_max)
    x_right = x_left + self.pixels_per_x_unit * (diff_mins_max - diff_mins_min)
    self.canvas.rectangle((x_left, y_top, x_right, y_bottom), outline=0, fill=0)

  def draw(self):
    # Frame
    self.canvas.rectangle(
      (self.x_left, self.y_top, self.x_right, self.y_bottom), outline=0, fill=255)

    # Range lines
    y = self.get_y_by_value(180)
    self.canvas.line((self.x_left, y, self.x_right, y), fill=0, width=0)
    y = self.get_y_by_value(70)
    self.canvas.line((self.x_left, y, self.x_right, y), fill=0, width=0)

    # Y-Scales
    self.draw_y_scale(self.y_max)
    self.draw_y_scale(180)
    self.draw_y_scale(70)
    self.draw_y_scale(self.y_min)

    # X-Scales
    self.draw_x_scale(60, offset=40)
    self.draw_x_scale(120, offset=40)

    self.draw_block(diff_mins_min=0, diff_mins_max=15, value=80)
    self.draw_block(diff_mins_min=15, diff_mins_max=30, value=100)
    self.draw_block(diff_mins_min=30, diff_mins_max=45, value=90)
    self.draw_block(diff_mins_min=45, diff_mins_max=60, value=95)
    self.draw_block(diff_mins_min=60, diff_mins_max=75, value=118)
    self.draw_block(diff_mins_min=75, diff_mins_max=90, value=143)
    self.draw_block(diff_mins_min=90, diff_mins_max=105, value=198)
    self.draw_block(diff_mins_min=105, diff_mins_max=120, value=212)
    self.draw_block(diff_mins_min=120, diff_mins_max=135, value=208)
    self.draw_block(diff_mins_min=135, diff_mins_max=150, value=219)
    self.draw_block(diff_mins_min=150, diff_mins_max=165, value=230)
    self.draw_block(diff_mins_min=165, diff_mins_max=180, value=174)

