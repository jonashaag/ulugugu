from ulugugu import drawings, keys
from ulugugu.events import ACK, KeyPress, send_event, event_used
from ulugugu.widgets import *
from ulugugu.utils import rect_in_rect


class Workspace(Container):
  def __init__(self, width, height):
    self.width = lambda: width
    self.height = lambda: height
    self.focused_child = None
    self.children = []

  def update_child_positions(self):
    pass

  def can_add_child(self, positioned_child):
    return True

  def draw(self, ctx):
    super().draw(ctx)
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0.7, 0.7, 0.7),
      fill='stroke'
    ).draw(ctx)
    drawings.Text(str(len(self.children))).draw(ctx)

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
