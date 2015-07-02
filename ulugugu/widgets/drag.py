from ulugugu.widgets import WidgetWrapper
from ulugugu.events import Event, send_event


class DragEvent(Event):
  def __init__(self, last_x, last_y):
    self.last_x = last_x
    self.last_y = last_y

  def for_child(self, child_x, child_y):
    return super().for_child(child_x, child_y).clone(
      last_x = self.last_x - child_x,
      last_y = self.last_y - child_y,
    )


class Drag(DragEvent):
  def __init__(self, xrel, yrel, last_x, last_y):
    super().__init__(last_x, last_y)
    self.xrel = xrel
    self.yrel = yrel


class DragStart(DragEvent):
  pass


class DragStop(DragEvent):
  pass


class ReceiveChild(Event):
  def __init__(self, child, child_xoff, child_yoff):
    self.child = child
    self.child_xoff = child_xoff
    self.child_yoff = child_yoff


class UnparentChild(Event):
  def __init__(self, former_parent, child, child_xoff, child_yoff):
    self.former_parent = former_parent
    self.child = child
    self.child_xoff = child_xoff
    self.child_yoff = child_yoff


class DragWrapper(WidgetWrapper):
  def __init__(self, child):
    super().__init__(child)
    self.drag_started = False
    self.drag_origin_x = None
    self.drag_origin_y = None

  def on_MousePress(self, event, event_ctx):
    self.drag_origin_x = event_ctx.mouse_x
    self.drag_origin_y = event_ctx.mouse_y
    return send_event(self.child, event, event_ctx)

  def on_MouseRelease(self, event, event_ctx):
    if self.drag_started:
      self.drag_started = False
      send_event(self.child, DragStop(*self._drag_info()), event_ctx)
    self.drag_origin_x = self.drag_origin_y = None
    return send_event(self.child, event, event_ctx)

  def on_MouseMove(self, event, event_ctx):
    if self.drag_origin_x is None:
      return send_event(self.child, event, event_ctx)
    else:
      if not self.drag_started:
        self.drag_started = True
        send_event(self.child, DragStart(*self._drag_info()), event_ctx)
      drag_event = Drag(event.xrel, event.yrel, *self._drag_info())
      self.drag_origin_x = event_ctx.mouse_x
      self.drag_origin_y = event_ctx.mouse_y
      return send_event(self.child, drag_event, event_ctx)

  def _drag_info(self):
    return self.drag_origin_x, self.drag_origin_y
