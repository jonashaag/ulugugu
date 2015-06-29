import abc
from . import Cloneable

class Drawing(Cloneable, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def draw(self, ctx):
    pass

  @abc.abstractmethod
  def width(self):
    # XXX remove
    pass

  @abc.abstractmethod
  def height(self):
    pass


class Empty(Drawing):
  def draw(self, ctx):
    pass

  def width(self):
    return 0

  def height(self):
    return 0


class MoveAbsolute(Drawing):
  def __init__(self, x, y, drawing):
    self.x = x
    self.y = y
    self.drawing = drawing

  def width(self):
    return 0

  def height(self):
    return 0

  def draw(self, ctx):
    with ctx:
      ctx.translate(self.x, self.y)
      return self.drawing.draw(ctx)

  def __repr__(self):
    return '<MoveAbsolute (%d,%d) %s>' % (self.x, self.y, self.drawing)


class Atop(Drawing):
  def __init__(self, foreground, background):
    self.foreground = foreground
    self.background = background

  def width(self):
    return max(self.foreground.width(), self.background.width())

  def height(self):
    return max(self.foreground.height(), self.background.height())

  def draw(self, ctx):
    with ctx:
      self.background.draw(ctx)
    with ctx:
      self.foreground.draw(ctx)

  def __repr__(self):
    return '<Atop %s>' % (self.foreground, self.background)


class Above(Drawing):
  def __init__(self, top, bottom, horizontal_alignment='left'):
    self.top = top
    self.bottom = bottom
    self.horizontal_alignment = horizontal_alignment

  def width(self):
    return max(self.top.width(), self.bottom.width())

  def height(self):
    return self.top.height() + self.bottom.height()

  def get_top_drawing_position(self):
    return (self.horizontal_displacement(self.top), 0)

  def get_bottom_drawing_position(self):
    return (self.horizontal_displacement(self.bottom), self.top.height())

  def draw(self, ctx):
    with ctx:
      ctx.translate(*self.get_top_drawing_position())
      self.top.draw(ctx)
    with ctx:
      ctx.translate(*self.get_bottom_drawing_position())
      self.bottom.draw(ctx)

  def horizontal_displacement(self, drawing):
    return {
      'left': 0,
      'center': (self.width() - drawing.width())/2,
      'right': self.width() - drawing.width(),
    }[self.horizontal_alignment]

  def __repr__(self):
    return '<Above %s>' % (self.top, self.bottom)


class Besides(Drawing):
  def __init__(self, left, right, vertical_alignment='top'):
    self.left = left
    self.right = right
    self.vertical_alignment = vertical_alignment

  def width(self):
    return self.left.width() + self.right.width()

  def height(self):
    return max(self.left.height(), self.right.height())

  def get_left_drawing_position(self):
    return (0, self.vertical_displacement(self.left))

  def get_right_drawing_position(self):
    return (self.left.width(), self.vertical_displacement(self.right))

  def draw(self, ctx):
    with ctx:
      ctx.translate(*self.get_left_drawing_position())
      self.left.draw(ctx)
    with ctx:
      ctx.translate(*self.get_right_drawing_position())
      self.right.draw(ctx)

  def vertical_displacement(self, drawing):
    return {
      'top': 0,
      'center': (self.height() - drawing.height())/2,
      'bottom': self.height() - drawing.height(),
    }[self.vertical_alignment]

  def __repr__(self):
    return '<Besides %s>' % (self.left, self.right)


class Rectangle(Drawing):
  def __init__(self, width, height, color, fill='fill'):
    super().__init__()
    self.color = color
    self.fill = fill
    self._width = width
    self._height = height

  def width(self):
    return self._width

  def height(self):
    return self._height

  def draw(self, ctx):
    ctx.set_source_rgb(*self.color)
    ctx.rectangle(0, 0, self.width(), self.height())
    getattr(ctx, self.fill)()

  def __repr__(self):
    return '<Rect w=%d h=%d c=%s>' % (self.width(), self.height(), self.color)


class Text(Drawing):
  def __init__(self, text):
    super().__init__()
    self.text = text

  def width(self):
    return len(self.text) * 8

  def height(self):
    return 15

  def draw(self, ctx):
    ctx.set_source_rgb(0,0,0)
    ctx.set_font_size(15)
    ctx.move_to(0, 15)
    ctx.show_text(self.text)
    ctx.new_path()

  def __repr__(self):
    return '<Text %r>' % self.text
