from ulugugu.events import Event
from ulugugu import drawings, vec2
from ulugugu.widgets import Widget, WidgetWrapper, Move
from ulugugu.widgets.drag import UnparentChild, ResendRequest
from ulugugu.utils import cursor_over_drawing
from ulugugu.events import ACK, send_event, event_used


class Swap(Event):
  def __init__(self, new_widget, event_response):
    self.new_widget = new_widget
    self.event_response = event_response


class SwapWidget(WidgetWrapper):
  def on_unhandled_event(self, event, event_ctx):
    response = send_event(self.child, event, event_ctx)
    if isinstance(response, Swap):
      self.child = response.new_widget
      response = response.event_response
    return response


def filled_droparea_drawing(child_drawing_size):
  w, h = child_drawing_size
  return drawings.Rectangle(
    (max(50, w), max(50, h)),
    (0.5, 0.5, 0.5),
    fill='stroke'
  )


class EmptyDropArea(Widget):
  def value(self):
    return None

  def get_drawing(self):
    return drawings.Rectangle((50, 50), (0.8, 0.8, 0.8))

  def on_ReceiveChild(self, event, event_ctx):
    return Swap(SemiFilledDropArea(event.child.get_drawing().boundingbox.size()), ResendRequest())

  on_KeyPress_default = Widget.ignore
  on_MousePress = Widget.ignore
  on_MouseRelease = Widget.ignore
  on_MouseMove = Widget.ignore
  on_DragStart = Widget.ignore
  on_DragStop = Widget.ignore
  on_Drag = Widget.ignore


class SemiFilledDropArea(Widget):
  def __init__(self, child_drawing_size):
    self.child_drawing_size = child_drawing_size

  def value(self):
    return None

  def get_drawing(self):
    return filled_droparea_drawing(self.child_drawing_size)

  def on_ReceiveChild(self, event, event_ctx):
    return Swap(
      FilledDropArea(
        Move(
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
    area_drawing = filled_droparea_drawing(child_drawing.boundingbox.size())
    return drawings.Atop(child_drawing, area_drawing) \
              .clone(boundingbox=area_drawing.boundingbox)

  def forward_event_to_child(self, event, event_ctx):
    response = send_event(self.child.widget, event.for_child(self.child.offset),
                                             event_ctx.for_child(self.child.offset))
    if event_used(response):
      self._center_child()
    return response

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
    if cursor_over_drawing(self.child.get_drawing(), event_ctx):
      self.dragging = True
    return self.forward_event_to_child(event, event_ctx)

  def on_Drag(self, event, event_ctx):
    if not self.dragging:
      return

    response = self.forward_event_to_child(event, event_ctx)
    if event_used(response):
      return response

    self._move_child(event.relative_movement)
    # Cursor out of bounding box?
    if not cursor_over_drawing(self.get_drawing(), event_ctx):
      return Swap(
        EmptyDropArea(),
        UnparentChild(
          child         = self.child.widget,
          child_offset  = vec2.sub(event_ctx.mouse_position, self.child.offset)
        )
      )
    else:
      return ACK

  def on_DragStop(self, event, event_ctx):
    self.dragging = False
    self._center_child()
    return self.forward_event_to_child(event, event_ctx)

  def _move_child(self, offset):
    self.child = Move.simplify(Move(self.child, offset))

  def _center_child(self):
    self_boundingbox = self.get_drawing().boundingbox
    child_boundingbox = self.child.get_drawing().boundingbox
    offset = child_boundingbox.align_displacement((0.5, 0.5))
    offset = vec2.add(offset, (self_boundingbox.width()/2, self_boundingbox.height()/2))
    self._move_child(offset)


class DropArea(SwapWidget):
  def __init__(self):
    super().__init__(EmptyDropArea())
