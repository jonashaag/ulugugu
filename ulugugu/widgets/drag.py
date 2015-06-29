from ulugugu.widgets import WidgetWrapper
from ulugugu.events import Event, send_event


class Drag(Event):
  def __init__(self, start_x, start_y, xrel, yrel):
    self.start_x = start_x
    self.start_y = start_y
    self.xrel = xrel
    self.yrel = yrel


class DragStart(Event):
  pass


class DragStop(Event):
  pass


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
      send_event(self.child, DragStop(), event_ctx)
    self.drag_origin_x = self.drag_origin_y = None
    return send_event(self.child, event, event_ctx)

  def on_MouseMove(self, event, event_ctx):
    if self.drag_origin_x is None:
      return send_event(self.child, event, event_ctx)
    else:
      if not self.drag_started:
        self.drag_started = True
        send_event(self.child, DragStart(), event_ctx)
      drag_event = Drag(self.drag_origin_x, self.drag_origin_y, event.xrel, event.yrel)
      return send_event(self.child, drag_event, event_ctx)
