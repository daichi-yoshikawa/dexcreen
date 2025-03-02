from PIL import Image, ImageDraw

from canvas import Canvas


class CgmChart:
  UNIT_MINS = 15

  def __init__(
      self, epd, height, width, x_offset=0, y_offset=0, display_hours=3,
      y_max=300, y_min=40, unit='mg/dL', background_color=255):
    self.height = height
    self.width = width

    self.canvas = Canvas(
      epd=epd, vertical=False, background_color=background_color)
    #self.image = Image.new('1', (height, width), background_color)
    #self.draw = ImageDraw.Draw(self.image)

    self.x_offset = x_offset
    self.y_offset = y_offset

    self.display_hours = display_hours

    self.y_max = y_max if unit == 'mg/dL' else round(y_max * 18)
    self.y_min = y_min if unit == 'mg/dL' else round(y_min * 18)

    self.unit = unit
    self.background_color = background_color

  @property
  def x_left(self):
    return self.x_offset

  @property
  def x_right(self):
    return self.x_offset + self.width

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
    return round(self.width / self.display_hours / 60 * self.UNIT_MINS)

  @property
  def pixels_per_y_unit(self):
    return round(self.height / (self.y_max - self.y_min) * self.y_unit)

  def draw(self):
    self.canvas.draw.rectangle((20, 240, 780, 460), outline=0, fill=128)
