from ulugugu import drawings
from ulugugu.widgets import Widget
from ulugugu.widgets.drag import UnparentChild
from ulugugu.utils import cursor_over_drawing
from ulugugu.events import ACK, send_event, event_used


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
    return self.drawing_combinator(self.fst.get_drawing(), self.snd.get_drawing())

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
    l, t, _, _ = self.get_child_drawing(child).boundingbox
    return send_event(child, event.for_child((l, t)), event_ctx.for_child((l, t)))

  def handle_child_response(self, response, event_ctx):
    if response is ACK:
      return ACK
    elif isinstance(response, UnparentChild):
      return response.clone(former_parent=self)
    else:
      raise TypeError("Don't know how to deal with child response %s" % response)

  def get_child_under_cursor(self, event_ctx):
    for child in [self.fst, self.snd]:
      if cursor_over_drawing(self.get_child_drawing(child), event_ctx):
        return child

  def get_child_drawing(self, child):
    drawing = self.get_drawing()
    if child is self.fst:
      return drawing.children[0]
    else:
      return drawing.children[1]


class Besides(Atop):
  drawing_combinator = drawings.Besides

class Above(Atop):
  drawing_combinator = drawings.Above
