from PIL import Image, ImageDraw

class CgmChartImage:
  def __init__(
      self, height, width, x_offset=0, y_offset=0, unit_mins=0.25,
      displayed_hours=3,  y_unit=10, y_min=40, unit='mg/dL', background_color=255):
    self.height = height
    self.width = width

    self.image = Image.new('1', (height, width), background_color)
    self.draw = ImageDraw.Draw(self.image)

    self.x_offset = x_offset
    self.y_offset = y_offset

    self.unit_mins = unit_mins
    self.displayed_hours = displayed_hours

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
  def pixels_per_sec(self):
    return round(self.width / self.displayed_hours / self.x_unit)

  @property
  def pixels_per_y_unit(self):
    return round(self.height / (self.y_max - self.y_min) * self.y_unit)

  @property
  def x_unit_seconds(self):
    return round(60 * 60 * self.x_unit)

