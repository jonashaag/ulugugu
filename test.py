from ulugugu import sdl, drawings, keys
from ulugugu.widgets import *
from ulugugu.events import Event, ACK, send_event, event_used


class BesidesWidget(Container):
  can_move_children = False

  def __init__(self, left, right):
    self.width = lambda: left.width() + right.width()
    self.height = lambda: max(left.height(), right.height())
    self.focused_child = None
    self.children = [PositionedChild(left, 0, 0),
                     PositionedChild(right, left.width(), 0)]

  def can_add_child(self, positioned_child):
    return False

  def update_child_positions(self):
    self.children[1].x = self.children[0].inner.width()

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


class DropArea(Container):
  empty_width = 50
  empty_height = 50
  empty_color = (0.8, 0.8, 0.8)

  border_width = 2
  border_height = 2
  border_color = (0.5, 0.5, 0.5)

  def __init__(self):
    self.children = []
    self.focused_child = None

  def update_child_positions(self):
    if self.children:
      center_x = self.width()/2 - self.children[0].inner.width()/2
      center_y = self.height()/2 - self.children[0].inner.height()/2
      self.children[0].x = center_x
      self.children[0].y = center_y

  def can_add_child(self, positioned_child):
    return not self.children

  def width(self):
    if not self.children:
      return self.empty_width
    else:
      return max(self.empty_width, self.children[0].inner.width() + 2 * self.border_width)

  def height(self):
    if not self.children:
      return self.empty_height
    else:
      return max(self.empty_height, self.children[0].inner.height() + 2 * self.border_height)

  def on_DragStop(self, event, event_ctx):
    self.update_child_positions()

  def draw(self, ctx):
    if not self.children:
      drawings.Rectangle(
        self.empty_width,
        self.empty_height,
        self.empty_color
      ).draw(ctx)
    else:
      drawings.Rectangle(
        self.width(),
        self.height(),
        self.border_color,
        fill='stroke'
      ).draw(ctx)
      with ctx:
        super().draw(ctx)


class ProgramState:
  def __init__(self, rootobj):
    self.rootobj = rootobj

  def handle_event(self, event, event_ctx):
    return send_event(self.rootobj, event, event_ctx)

  def draw(self, ctx):
    with ctx:
      ctx.set_source_rgb(1,1,1)
      ctx.paint()
    self.rootobj.draw(ctx)


workspace = Workspace(700, 500)
workspace2 = Workspace(200, 200)
workspace2.children.append(PositionedChild(Workspace(100, 100), 20, 20))
workspace.children.append(PositionedChild(BesidesWidget(workspace2, DropArea()), 150, 150))
workspace.children.append(PositionedChild(DropArea(), 400, 300))
workspace.children.append(PositionedChild(BesidesWidget(IntegerInput(), BesidesWidget(DropArea(), DropArea())), 10, 10))
workspace.children.append(PositionedChild(Workspace(200, 200), 400, 400))
sdl.main(ProgramState(DragWrapper(workspace)))
