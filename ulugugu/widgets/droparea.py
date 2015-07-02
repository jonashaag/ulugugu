from ulugugu import drawings
from ulugugu.widgets import Widget, Swap, SwapWidget
from ulugugu.widgets.drag import UnparentChild
from ulugugu.widgets.container import PositionedChild
from ulugugu.utils import pt_in_rect
from ulugugu.events import ACK, send_event, event_used


class EmptyDropArea(Widget):
  def value(self):
    return None

  def get_drawing(self):
    return drawings.Rectangle(50, 50, (0.8, 0.8, 0.8))

  def on_ReceiveChild(self, event, event_ctx):
    return Swap(
      FilledDropArea(
        PositionedChild(
          event.child,
          event_ctx.mouse_x - event.child_xoff,
          event_ctx.mouse_y - event.child_yoff,
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
    return drawings.Atop(
      drawings.MoveAbsolute(self.child.x, self.child.y, child_drawing),
      drawings.Rectangle(
        max(50, child_drawing.width()),
        max(50, child_drawing.height()),
        (0.5, 0.5, 0.5),
        fill='stroke'
      )
    )

  def forward_event_to_child(self, event, event_ctx):
    return send_event(self.child.child, event.for_child(self.child.x, self.child.y),
                                        event_ctx.for_child(self.child.x, self.child.y))

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
    if pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, self.child.x, self.child.y, self.child.width(), self.child.height()):
      self.dragging = True
    return self.forward_event_to_child(event, event_ctx)

  def on_Drag(self, event, event_ctx):
    if not self.dragging:
      return

    response = self.forward_event_to_child(event, event_ctx)
    if event_used(response):
      return response

    self.child.move_relative(event.xrel, event.yrel)
    # Cursor out of bounding box?
    if not pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, 0, 0, self.get_drawing().width(), self.get_drawing().height()):
      return Swap(
        EmptyDropArea(),
        UnparentChild(
          former_parent = self,
          child         = self.child.child,
          child_xoff    = event_ctx.mouse_x - self.child.x,
          child_yoff    = event_ctx.mouse_y - self.child.y,
        )
      )
    else:
      return ACK

  def on_DragStop(self, event, event_ctx):
    self.dragging = False
    return self.forward_event_to_child(event, event_ctx)


class DropArea(SwapWidget):
  def __init__(self):
    super().__init__(EmptyDropArea())
