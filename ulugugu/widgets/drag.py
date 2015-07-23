from ulugugu import vec2
from ulugugu.widgets import WidgetWrapper
from ulugugu.events import Event, send_event


class DragEvent(Event):
  def __init__(self, previous_position):
    self.previous_position = previous_position

  def for_child(self, child_position):
    return super().for_child(child_position).clone(
      previous_position=vec2.sub(self.previous_position, child_position)
    )


class Drag(DragEvent):
  def __init__(self, relative_movement, previous_mouse_position):
    super().__init__(previous_mouse_position)
    self.relative_movement = relative_movement


class DragStart(DragEvent):
  pass


class DragStop(DragEvent):
  pass


class ReceiveChild(Event):
  def __init__(self, child, child_offset):
    self.child = child
    self.child_offset = child_offset


class UnparentChild(Event):
  def __init__(self, child, child_offset):
    self.child = child
    self.child_offset = child_offset


class DragWrapper(WidgetWrapper):
  def __init__(self, child):
    super().__init__(child)
    self.drag_started = False
    self.drag_origin = None

  def on_MousePress(self, event, event_ctx):
    self.drag_origin = event_ctx.mouse_position
    return send_event(self.child, event, event_ctx)

  def on_MouseRelease(self, event, event_ctx):
    if self.drag_started:
      self.drag_started = False
      send_event(self.child, DragStop(self.drag_origin), event_ctx)
    self.drag_origin = None
    return send_event(self.child, event, event_ctx)

  def on_MouseMove(self, event, event_ctx):
    if self.drag_origin is None:
      return send_event(self.child, event, event_ctx)
    else:
      if not self.drag_started:
        self.drag_started = True
        send_event(self.child, DragStart(self.drag_origin), event_ctx)
      drag_event = Drag(event.relative_movement, self.drag_origin)
      self.drag_origin = event_ctx.mouse_position
      return send_event(self.child, drag_event, event_ctx)
