from . import Cloneable

class Drawing(Cloneable):
  def __init__(self):
    self.x = 0
    self.y = 0

  def move(self, xoff, yoff):
    return self.clone(x=self.x+xoff, y=self.y+yoff)

  def draw(self, ctx):
    ctx.translate(self.x, self.y)
    self._draw(ctx)


class Rectangle(Drawing):
  def __init__(self, width, height, color, fill='fill'):
    super().__init__()
    self.w = width
    self.h = height
    self.color = color
    self.fill = fill

  def _draw(self, ctx):
    ctx.set_source_rgb(*self.color)
    ctx.rectangle(0, 0, self.w, self.h)
    getattr(ctx, self.fill)()


class Text(Drawing):
  def __init__(self, text):
    super().__init__()
    self.text = text

  def _draw(self, ctx):
    ctx.set_source_rgb(0,0,0)
    ctx.set_font_size(15)
    ctx.move_to(0, 15)
    ctx.show_text(self.text)
    ctx.new_path()
