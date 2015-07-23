from ulugugu.drawings import Rectangle, Atop


class DebugBoundingBox(Atop):
  def __init__(self, drawing):
    l, t, _, _ = drawing.boundingbox
    border = Rectangle(drawing.size(), color=(0.5, 0.5, 0.5), fill='stroke').move((l, t))
    origin = Rectangle((6, 6), color=(1, 0, 0)).move_origin((3, 3))
    super().__init__(Atop(origin, border), drawing)
