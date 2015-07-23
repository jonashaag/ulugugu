import abc
from ulugugu import drawings, vec2
from ulugugu.events import send_event, event_used, ACK
from ulugugu.utils import cursor_over_drawing
from ulugugu.widgets.drag import UnparentChild


class Widget(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def value(self):
    pass

  @abc.abstractmethod
  def get_drawing(self):
    pass

  def handle_event(self, event, event_ctx):
    return self.dispatch_event(event, event_ctx)

  def dispatch_event(self, event, event_ctx):
    handler = self.get_event_handler(type(event).__name__)
    return handler(event, event_ctx)

  def get_event_handler(self, event_name):
    return getattr(self, 'on_%s' % event_name, self.on_unhandled_event)

  def on_unhandled_event(self, event, event_ctx):
    raise TypeError("%r misses handler for %r" % (type(self).__name__, type(event).__name__))

  def on_KeyPress(self, press, event_ctx):
    handler = getattr(self, 'on_KeyPress_%s' % press.key, None)
    if handler is None:
      handler = self.get_event_handler('KeyPress_default')
      return handler(press, event_ctx)
    else:
      return handler(event_ctx)

  def ignore(self, event, event_ctx):
    pass


class WidgetWrapper(Widget):
  def __init__(self, child):
    self.child = child

  def on_unhandled_event(self, event, event_ctx):
    return send_event(self.child, event, event_ctx)

  def value(self):
    return self.child.value()

  def get_drawing(self):
    return self.child.get_drawing()


class Move(Widget):
  def __init__(self, widget, offset):
    self.widget = widget
    self.offset = offset

  def value(self):
    return self.widget.value()

  def get_drawing(self):
    return drawings.Move(self.widget.get_drawing(), self.offset)

  def on_unhandled_event(self, event, event_ctx):
    return send_event(self.widget, event.for_child(self.offset), event_ctx.for_child(self.offset))

  @staticmethod
  def simplify(widget):
    inner_widget = widget.widget
    if isinstance(inner_widget, Move):
      widget = Move(inner_widget.widget, vec2.add(widget.offset, inner_widget.offset))
    return widget


class Align(Widget):
  def __init__(self, widget, alignment):
    self.widget = widget
    self.alignment = alignment

  def value(self):
    return self.widget.value()

  def get_drawing(self):
    return drawings.Move(self.widget.get_drawing(), self.get_offset())

  def on_unhandled_event(self, event, event_ctx):
    return send_event(self.widget, event.for_child(self.get_offset()), event_ctx.for_child(self.get_offset()))

  def get_offset(self):
    return self.widget.get_drawing().boundingbox.align_displacement(self.alignment)


class Atop(Widget):
  drawing_combinator = drawings.Atop

  def __init__(self, fst, snd):
    self.fst = fst
    self.snd = snd
    self.focused_child = None
    self.dragging = None

  def value(self):
    return self.fst.value(), self.snd.value()

  def get_drawing(self):
    return self.drawing_combinator(
      self.fst.get_drawing(),
      drawings.Move(self.snd.get_drawing(), self.get_snd_child_offset()),
    )

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
    if child is self.snd:
      event = event.for_child(self.get_snd_child_offset())
      event_ctx = event_ctx.for_child(self.get_snd_child_offset())
    return send_event(child, event, event_ctx)

  def handle_child_response(self, response, event_ctx):
    if response is ACK:
      return ACK
    elif isinstance(response, UnparentChild):
      return response.clone(former_parent=self)
    else:
      raise TypeError("Don't know how to deal with child response %s" % response)

  def get_child_under_cursor(self, event_ctx):
    for child, offset in [
      (self.fst, (0, 0)),
      (self.snd, self.get_snd_child_offset()),
    ]:
      if cursor_over_drawing(child.get_drawing(), event_ctx, offset):
        return child

  def get_snd_child_offset(self):
    return (0, 0)


class Above(Atop):
  def get_snd_child_offset(self):
    _, _, _, b = self.fst.get_drawing().boundingbox
    _, t, _, _ = self.snd.get_drawing().boundingbox
    return (0, b - t)


class Besides(Atop):
  def get_snd_child_offset(self):
    _, _, r, _ = self.fst.get_drawing().boundingbox
    l, _, _, _ = self.snd.get_drawing().boundingbox
    return (r - l, 0)
