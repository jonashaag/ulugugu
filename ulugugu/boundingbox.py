class BoundingBox(tuple):
  def atop(self, other):
    l1, t1, r1, b1 = self
    l2, t2, r2, b2 = other
    return BoundingBox((min(l1, l2), min(t1, t2), max(r1, r2), max(b1, b2)))

  def move(self, offset):
    l, t, r, b = self
    x, y = offset
    return BoundingBox((l+x, t+y, r+x, b+y))

  def width(self):
    l, _, r, _ = self
    return r - l

  def height(self):
    _, t, _, b = self
    return b - t

  def size(self):
    l, t, r, b = self
    return (r - l, b - t)

  def xalign_displacement(self, xalignment):
    if xalignment is None:
      return 0
    else:
      l, _, _, _ = self
      return -l - self.width() * xalignment

  def yalign_displacement(self, yalignment):
    if yalignment is None:
      return 0
    else:
      _, t, _, _ = self
      return -t - self.height() * yalignment

  def align_displacement(self, alignment):
    xalign, yalign = alignment
    return (self.xalign_displacement(xalign), self.yalign_displacement(yalign))

  #def align(self, alignment):
  #  return self.move(self.align_displacement(alignment))

  #def align_x(self, xalignment):
  #  return self.align((xalignment, None))

  #def align_y(self, yalignment):
  #  return self.align((None, yalignment))
