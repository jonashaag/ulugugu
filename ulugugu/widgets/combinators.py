from ulugugu import drawings
from ulugugu.widgets import *
from ulugugu.utils import pt_in_rect
from ulugugu.events import ACK, send_event, event_used


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
