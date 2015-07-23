import abc
from ulugugu import Cloneable


class Drawing(Cloneable, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def draw(self, ctx):
    pass

  def __init__(self, boundingbox):
    self.boundingbox = boundingbox


class Move(Drawing):
  def __init__(self, drawing, offset):
    super().__init__(drawing.boundingbox.move(offset))
    self.drawing = drawing
    self.offset = offset

  def draw(self, ctx):
    ctx.translate(*self.offset)
    self.drawing.draw(ctx)


class Align(Move):
  def __init__(self, drawing, alignment):
    super().__init__(drawing, drawing.boundingbox.align_displacement(alignment))


class Atop(Drawing):
  def __init__(self, fst, snd):
    super().__init__(fst.boundingbox.atop(snd.boundingbox))
    self.fst = fst
    self.snd = snd

  def draw(self, ctx):
    with ctx:
      self.snd.draw(ctx)
    with ctx:
      self.fst.draw(ctx)


class Above(Atop):
  def __init__(self, fst, snd):
    _, _, _, b = fst.boundingbox
    _, t, _, _ = snd.boundingbox
    snd = Move(snd, (0, b - t))
    super().__init__(fst, snd)


class Besides(Atop):
  def __init__(self, fst, snd):
    _, _, r, _ = fst.boundingbox
    l, _, _, _ = snd.boundingbox
    snd = Move(snd, (r - l, 0))
    super().__init__(fst, snd)
