from ulugugu import drawings
from ulugugu.widgets import Widget, WidgetWrapper
from ulugugu.widgets.drag import UnparentChild
from ulugugu.utils import pt_in_rect
from ulugugu.events import ACK, send_event, event_used


class ChangeDrawing(WidgetWrapper):
  def handle_event(self, event, event_ctx):
    child_x, child_y = self.get_child_position()
    event = event.for_child(child_x, child_y)
    event_ctx = event_ctx.for_child(child_x, child_y)
    return super().handle_event(event, event_ctx)


class BesidesAboveWidget(Widget):
  def __init__(self, left, right):
    self.left = left
    self.right = right
    self.focused_child = None
    self.dragging = None

  def value(self):
    return self.left.value(), self.right.value()

  def forward_event_to_focused_child(self, event, event_ctx, *args, **kwargs):
    return self.forward_event_to_child(self.focused_child, event, event_ctx, *args, **kwargs)

  def forward_event_to_child_under_cursor(self, event, event_ctx, *args, **kwargs):
    return self.forward_event_to_child(self.get_child_under_cursor(event_ctx),
                                       event, event_ctx, *args, **kwargs)

  on_KeyPress_default = forward_event_to_focused_child
  on_MouseRelease     = forward_event_to_focused_child
  on_MouseMove        = forward_event_to_child_under_cursor

  def on_MousePress(self, event, event_ctx):
    def on_child_response(child, response):
      self.focused_child = child
    return self.forward_event_to_child_under_cursor(event, event_ctx, on_child_response)

  def on_ReceiveChild(self, event, event_ctx):
    def on_child_response(child, response):
      self.focused_child = child
      self.dragging = True
    return self.forward_event_to_child_under_cursor(event, event_ctx, on_child_response)

  def on_DragStart(self, event, event_ctx):
    child = self.get_child_under_cursor(event_ctx)
    self.dragging = child is not None
    return self.forward_event_to_child(child, event, event_ctx)

  def on_Drag(self, event, event_ctx):
    if self.dragging:
      return self.forward_event_to_focused_child(event, event_ctx)

  def on_DragStop(self, event, event_ctx):
    self.dragging = None
    return self.forward_event_to_focused_child(event, event_ctx)

  def forward_event_to_child(self, child, event, event_ctx, on_child_response=None):
    if child is None:
      return
    response = self.send_event_child(child, event, event_ctx)
    if event_used(response):
      if on_child_response is not None:
        on_child_response(child, response)
      return self.handle_child_response(response, event_ctx)

  def send_event_child(self, child, event, event_ctx):
    x, y = self.get_child_position(child)
    return send_event(self.get_child(child), event.for_child(x, y), event_ctx.for_child(x, y))

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
