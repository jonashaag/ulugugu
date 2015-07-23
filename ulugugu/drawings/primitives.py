from ulugugu import BBox
from ulugugu.drawings import Drawing


class Empty(Drawing):
  def __init__(self):
    super().__init__(BBox((0, 0, 0, 0)))

  def draw(self, ctx):
    pass


class Rectangle(Drawing):
  def __init__(self, size, color, fill='fill'):
    super().__init__(BBox((0, 0, size[0], size[1])))
    self.size = size
    self.color = color
    self.fill = fill

  def draw(self, ctx):
    ctx.set_source_rgb(*self.color)
    ctx.rectangle(0, 0, *self.size)
    getattr(ctx, self.fill)()


class Text(Drawing):
  def __init__(self, text):
    self.text = text
    super().__init__(BBox((0, -15, len(self.text)*8, 0)))

  def draw(self, ctx):
    ctx.set_source_rgb(0,0,0)
    ctx.set_font_size(15)
    ctx.show_text(self.text)
    ctx.new_path()
