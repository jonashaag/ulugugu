from ulugugu import drawings, keys
from ulugugu.events import ACK, KeyPress, send_event, event_used
from ulugugu.widgets import *
from ulugugu.utils import rect_in_rect


class Workspace(Container):
  def __init__(self, width, height):
    super().__init__()
    self._width = width
    self._height = height

  def value(self):
    pass

  def get_drawing(self):
    border = drawings.Rectangle(
      width=self._width,
      height=self._height,
      color=(0.7, 0.7, 0.7),
      fill='stroke'
    )
    child_counter = drawings.Text(str(len(self.children)))
    return drawings.Atop(
      drawings.Above(child_counter, border),
      super().get_drawing()
    )

  def update_child_positions(self):
    pass

  def can_add_child(self, positioned_child):
    return True

  def on_KeyPress_CHAR_T(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_T), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.children.append(PositionedChild(StringInput("Some text"), 100, 100))
    return ACK

  def on_KeyPress_CHAR_I(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_I), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.children.append(PositionedChild(IntegerInput(), 100, 100))
    return ACK

  def on_KeyPress_ESCAPE(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.ESCAPE), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
      else:
        self.focused_child = None
        return ACK
