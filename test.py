from ulugugu import sdl, drawings, keys, values
from ulugugu.widgets import *
from ulugugu.events import Event, ACK, send_event, event_used


class DropArea(Container):
  empty_width = 50
  empty_height = 50
  empty_color = (0.8, 0.8, 0.8)

  border_width = 2
  border_height = 2
  border_color = (0.5, 0.5, 0.5)

  def update_child_positions(self):
    if self.children:
      center_x = self.width()/2 - self.children[0].width()/2
      center_y = self.height()/2 - self.children[0].height()/2
      self.children[0].x = center_x
      self.children[0].y = center_y

  def can_add_child(self, positioned_child):
    return not self.children

  def value(self):
    if self.children:
      return self.children[0].value()

  def width(self):
    if not self.children:
      return self.empty_width
    else:
      return max(self.empty_width, self.children[0].width() + 2 * self.border_width)

  def height(self):
    if not self.children:
      return self.empty_height
    else:
      return max(self.empty_height, self.children[0].height() + 2 * self.border_height)

  def on_DragStop(self, event, event_ctx):
    self.update_child_positions()
    return super().on_DragStop(event, event_ctx)

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


class ApplicationWidget(AboveWidget):
  def __init__(self):
    super().__init__(DropArea(), BesidesWidget(DropArea(), DropArea()), horizontal_alignment='center')

  def value(self):
    return values.Application(self.children[0].value(), *self.children[1].value())


class ShowValueWidget(WidgetWrapper):
  def height(self):
    return self.child.height() + 15

  def draw(self, ctx):
    drawings.Text(str(self.value())).draw(ctx)
    ctx.translate(0, 15)
    self.child.draw(ctx)


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
workspace.children.append(PositionedChild(ShowValueWidget(ApplicationWidget()), 100, 100))
sdl.main(ProgramState(DragWrapper(workspace)))
