import abc
from ulugugu import Cloneable, vec2


class Drawing(Cloneable, metaclass=abc.ABCMeta):
  def __init__(self, boundingbox):
    self.boundingbox = boundingbox

  @abc.abstractmethod
  def draw(self, ctx):
    pass

  @property
  def width(self):
    l, _, r, _ = self.boundingbox
    return r - l

  @property
  def height(self):
    _, t, _, b = self.boundingbox
    return b - t

  @property
  def size(self):
    return self.width, self.height

  def move_origin(self, offset):
    return self.move(vec2.neg(offset))

  def move(self, offset):
    xoff, yoff = offset
    l, t, r, b = self.boundingbox
    return self.clone(boundingbox=(l+xoff, t+yoff, r+xoff, b+yoff))

  def set_boundingbox(self, new_boundingbox):
    return self.clone(boundingbox=new_boundingbox)

  def align(self, horizontal, vertical):
    return self.align_horizontal(horizontal) \
               .align_vertical(vertical)

  def align_horizontal(self, alignment):
    _, t, _, b = self.boundingbox
    x = self.width * alignment
    return self.set_boundingbox((-x, t, -x+self.width, b))

  def align_vertical(self, alignment):
    l, _, r, _ = self.boundingbox
    y = self.height * alignment
    return self.set_boundingbox((l, -y, r, -y+self.height))


class Empty(Drawing):
  def __init__(self):
    super().__init__((0, 0, 0, 0))

  def draw(self, ctx):
    pass


class Rectangle(Drawing):
  def __init__(self, size, color, fill='fill'):
    w, h = size
    super().__init__((0, 0, w, h))
    self.color = color
    self.fill = fill

  def draw(self, ctx):
    ctx.set_source_rgb(*self.color)
    l, t, _, _ = self.boundingbox
    ctx.rectangle(l, t, self.width, self.height)
    getattr(ctx, self.fill)()


class Text(Drawing):
  def __init__(self, text):
    self.text = text
    super().__init__((0, -15, len(self.text)*8, 0))

  def draw(self, ctx):
    l, t, *_ = self.boundingbox
    ctx.set_source_rgb(0,0,0)
    ctx.set_font_size(15)
    ctx.move_to(l, t+15)
    ctx.show_text(self.text)
    ctx.new_path()

  def __repr__(self):
    return '<Text %r>' % self.text


class Atop(Drawing):
  def __init__(self, fst, snd):
    l1, t1, r1, b1 = fst.boundingbox
    l2, t2, r2, b2 = snd.boundingbox
    super().__init__((min(l1, l2), min(t1, t2), max(r1, r2), max(b1, b2)))
    self.children = (fst, snd)

  def move(self, offset):
    return super().move(offset).clone(children=(self.children[0].move(offset),
                                                self.children[1].move(offset)))

  def draw(self, ctx):
    for child in reversed(self.children):
      with ctx:
        child.draw(ctx)

  def __repr__(self):
    return '<%s %s>' % (self.__class__.__name__, self.children)


class Above(Atop):
  def __init__(self, top, bottom):
    _, _, _, b = top.boundingbox
    _, t, _, _ = bottom.boundingbox
    super().__init__(top, bottom.move((0, b - t)))


class Besides(Atop):
  def __init__(self, left, right):
    _, _, r, _ = left.boundingbox
    l, _, _, _ = right.boundingbox
    super().__init__(left, right.move((r - l, 0)))


class DebugBoundingBox(Atop):
  def __init__(self, drawing):
    l, t, _, _ = drawing.boundingbox
    border = Rectangle(drawing.size, color=(0.5, 0.5, 0.5), fill='stroke').move((l, t))
    origin = Rectangle((6, 6), color=(1, 0, 0)).move_origin((3, 3))
    super().__init__(Atop(origin, border), drawing)
