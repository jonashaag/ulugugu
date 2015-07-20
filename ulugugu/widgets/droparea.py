from ulugugu import drawings, vec2
from ulugugu.widgets import Widget, Swap, SwapWidget
from ulugugu.widgets.drag import UnparentChild
from ulugugu.widgets.container import PositionedChild
from ulugugu.utils import cursor_over_drawing
from ulugugu.events import ACK, send_event, event_used


class EmptyDropArea(Widget):
  def value(self):
    return None

  def get_drawing(self):
    return drawings.Rectangle((50, 50), (0.8, 0.8, 0.8))

  def on_ReceiveChild(self, event, event_ctx):
    return Swap(
      FilledDropArea(
        PositionedChild(
          event.child,
          vec2.sub(event_ctx.mouse_position, event.child_offset),
        )
      ),
      ACK
    )

  on_KeyPress_default = Widget.ignore
  on_MousePress = Widget.ignore
  on_MouseRelease = Widget.ignore
  on_MouseMove = Widget.ignore
  on_DragStart = Widget.ignore
  on_DragStop = Widget.ignore
  on_Drag = Widget.ignore


class FilledDropArea(Widget):
  def __init__(self, child):
    self.child = child
    self.dragging = True

  def value(self):
    return self.child.value()

  def get_drawing(self):
    child_drawing = self.child.get_drawing()
    area_drawing = drawings.Rectangle(
      (max(50, child_drawing.width), max(50, child_drawing.height)),
      (0.5, 0.5, 0.5),
      fill='stroke'
    )
    return drawings.Atop(child_drawing.move(self.child.position), area_drawing) \
              .clone(boundingbox=area_drawing.boundingbox)

  def forward_event_to_child(self, event, event_ctx):
    return send_event(self.child.child, event.for_child(self.child.position),
                                        event_ctx.for_child(self.child.position))

  on_KeyPress_default = forward_event_to_child
  on_MousePress       = forward_event_to_child
  on_MouseRelease     = forward_event_to_child
  on_MouseMove        = forward_event_to_child

  def on_ReceiveChild(self, event, event_ctx):
    response = self.forward_event_to_child(event, event_ctx)
    if event_used(response):
      self.dragging = True
    return response

  def on_DragStart(self, event, event_ctx):
    if cursor_over_drawing(self.child.get_drawing(), event_ctx, self.child.position):
      self.dragging = True
    return self.forward_event_to_child(event, event_ctx)

  def on_Drag(self, event, event_ctx):
    if not self.dragging:
      return

    response = self.forward_event_to_child(event, event_ctx)
    if event_used(response):
      return response

    self.child.move_relative(event.relative_movement)
    # Cursor out of bounding box?
    if not cursor_over_drawing(self.get_drawing(), event_ctx):
      return Swap(
        EmptyDropArea(),
        UnparentChild(
          former_parent = self,
          child         = self.child.child,
          child_offset  = vec2.sub(event_ctx.mouse_position, self.child.position)
        )
      )
    else:
      return ACK

  def on_DragStop(self, event, event_ctx):
    self.dragging = False
    self._center_child()
    return self.forward_event_to_child(event, event_ctx)

  def _center_child(self):
    drawing = self.get_drawing()
    child_drawing = self.child.get_drawing()
    l1, t1, _, _ = child_drawing.boundingbox
    l2, t2, _, _ = child_drawing.align(0.5, 0.5).boundingbox
    xcenter = drawing.width/2
    ycenter = drawing.height/2
    self.child.move(vec2.add((xcenter, ycenter), (l2-l1, t2-t1)))


class DropArea(SwapWidget):
  def __init__(self):
    super().__init__(EmptyDropArea())
