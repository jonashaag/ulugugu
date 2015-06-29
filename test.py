from ulugugu import sdl, drawings, keys, values
from ulugugu.widgets import *
from ulugugu.utils import pt_in_rect
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

  def on_DragStop(self, event, event_ctx):
    self.update_child_positions()
    return super().on_DragStop(event, event_ctx)

  def get_drawing(self):
    if self.children:
      return drawings.Atop(
        super().get_drawing(),
        drawings.Rectangle(
          max(self.empty_width, self.children[0].width()),
          max(self.empty_height, self.children[0].height()),
          self.border_color,
          fill='stroke'
        )
      )
    else:
      return drawings.Rectangle(
        self.empty_width,
        self.empty_height,
        self.empty_color
      )


class ApplicationWidget(object):
 def __init__(self):
   super().__init__(DropArea(), BesidesWidget(DropArea(), DropArea()), horizontal_alignment='center')

 def value(self):
   abstraction, *args = super().value()
   return values.Application(abstraction, *args)


class ShowValueWidget(WidgetWrapper):
  def get_drawing(self):
    return drawings.Above(
      drawings.Text(str(self.value())),
      self.child.get_drawing(),
    )


class ProgramState:
  def __init__(self, rootobj):
    self.rootobj = rootobj

  def handle_event(self, event, event_ctx):
    return send_event(self.rootobj, event, event_ctx)

  def draw(self, ctx):
    with ctx:
      ctx.set_source_rgb(1,1,1)
      ctx.paint()
    with ctx:
      self.rootobj.get_drawing().draw(ctx)


class BesidesAboveWidget(Widget):
  def __init__(self, left, right):
    self.left = left
    self.right = right
    self.focused_child = None

  def value(self):
    return self.left.value(), self.right.value()

  def forward_event_to_focused_child(self, event, event_ctx):
    if self.focused_child:
      return self.forward_event_to_child(self.focused_child, event, event_ctx)

  def forward_event_to_child_under_cursor(self, event, event_ctx):
    return self.forward_event_to_child(
      self.get_child_under_cursor(event_ctx),
      event,
      event_ctx
    )

  def forward_event_to_child_under_cursor_and_set_focused(self, event, event_ctx):
    child = self.get_child_under_cursor(event_ctx)
    response = self.send_event_child(child, event, event_ctx)
    if event_used(response):
      self.focused_child = child
      return self.handle_child_response(response, event_ctx)

  on_KeyPress_default = forward_event_to_focused_child
  on_MouseRelease     = forward_event_to_focused_child
  on_DragStart        = forward_event_to_focused_child
  on_Drag             = forward_event_to_focused_child
  on_DragStop         = forward_event_to_focused_child
  on_MouseMove        = forward_event_to_child_under_cursor
  on_MousePress       = forward_event_to_child_under_cursor_and_set_focused
  on_ReceiveChild     = forward_event_to_child_under_cursor_and_set_focused

  def forward_event_to_child(self, child, event, event_ctx):
    response = self.send_event_child(child, event, event_ctx)
    if event_used(response):
      return self.handle_child_response(response, event_ctx)

  def send_event_child(self, child, event, event_ctx):
    x, y = self.get_child_position(child)
    child_context = event_ctx.clone(
      mouse_x=event_ctx.mouse_x - x,
      mouse_y=event_ctx.mouse_y - y,
    )
    return send_event(self.get_child(child), event, child_context)

  def handle_child_response(self, response, event_ctx):
    if response is None:
      return
    else:
      if response is ACK:
        return ACK
      elif isinstance(response, UnparentChild):
        return response.clone(former_parent=self)
      else:
        raise TypeError("Don't know how to deal with child response %s" % response)

  def get_child(self, leftorright):
    if leftorright == 'left':
      return self.left
    elif leftorright == 'right':
      return self.right
    raise TypeError(leftorright)

  def get_child_under_cursor(self, event_ctx):
    for child in ['left', 'right']:
      child_widget = self.get_child(child)
      x, y = self.get_child_position(child)
      if pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, x, y, child_widget.width(), child_widget.height()):
        return child
    raise AssertionError("No child at (%d,%d)" % (event_ctx.mouse_x, event_ctx.mouse_y))


class Besides(BesidesAboveWidget):
  def get_drawing(self):
    return drawings.Besides(self.left.get_drawing(), self.right.get_drawing())

  def get_child_position(self, child):
    if child == 'left':
      return self.get_drawing().get_left_drawing_position()
    else:
      return self.get_drawing().get_right_drawing_position()


class Above(BesidesAboveWidget):
  def get_drawing(self):
    return drawings.Above(self.left.get_drawing(), self.right.get_drawing())

  def get_child_position(self, child):
    if child == 'left':
      return self.get_drawing().get_top_drawing_position()
    else:
      return self.get_drawing().get_bottom_drawing_position()


workspace = Workspace(700, 500)
# workspace.children.append(PositionedChild(ShowValueWidget(ApplicationWidget()), 100, 100))
workspace.children.append(PositionedChild(ShowValueWidget(StringInput("Test")), 100, 250))
workspace.children.append(PositionedChild(Besides(DropArea(), DropArea()), 100, 250))
workspace.children.append(PositionedChild(Above(DropArea(), DropArea()), 300, 250))
workspace.children.append(PositionedChild(DropArea(), 100, 100))
sdl.main(ProgramState(DragWrapper(workspace)))
