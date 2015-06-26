from ulugugu import drawings, values
from operator import methodcaller
from ulugugu.widgets import *


class AboveBesidesWidget(Container):
  can_move_children = False

  def __init__(self, child1, child2):
    super().__init__([child1, child2])

  def value(self):
    return self.children[0].value(), self.children[1].value()

  def can_add_child(self, positioned_child):
    return False

  def draw(self, ctx):
    super().draw(ctx)
    drawings.Rectangle(
      self.width(),
      self.height(),
      color=(0.9, 0.9, 0.9),
      fill='stroke'
    ).draw(ctx)
    with ctx:
      ctx.translate(self.width() - 20, 0)
      drawings.Text(str(len(self.children))).draw(ctx)


class BesidesWidget(AboveBesidesWidget):
  def __init__(self, left, right, vertical_alignment='top'):
    self.vertical_alignment = vertical_alignment
    super().__init__(
      PositionedChild(left, 0, 0),
      PositionedChild(right, left.width(), 0)
    )

  def width(self):
    return sum(map(methodcaller('width'), self.children))

  def height(self):
    return max(map(methodcaller('height'), self.children))

  def update_child_positions(self):
    self.children[0].y = self.calculate_vertical_displacement(self.children[0])
    self.children[1].y = self.calculate_vertical_displacement(self.children[1])
    self.children[1].x = self.children[0].width()

  def calculate_vertical_displacement(self, child):
    return {
      'top': 0,
      'center': (self.height() - child.height())/2,
      'bottom': self.height() - child.height(),
    }[self.vertical_alignment]


class AboveWidget(AboveBesidesWidget):
  def __init__(self, top, bottom, horizontal_alignment='left'):
    self.horizontal_alignment = horizontal_alignment
    super().__init__(
      PositionedChild(top, 0, 0),
      PositionedChild(bottom, 0, top.width())
    )

  def width(self):
    return max(map(methodcaller('width'), self.children))

  def height(self):
    return sum(map(methodcaller('height'), self.children))

  def update_child_positions(self):
    self.children[0].x = self.calculate_horizontal_displacement(self.children[0])
    self.children[1].x = self.calculate_horizontal_displacement(self.children[1])
    self.children[1].y = self.children[0].height()

  def calculate_horizontal_displacement(self, child):
    return {
      'left': 0,
      'center': (self.width() - child.width())/2,
      'right': self.width() - child.width(),
    }[self.horizontal_alignment]
