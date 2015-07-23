import time
from ulugugu import drawings, vec2
from ulugugu.events import ACK
from ulugugu.widgets import Widget, WidgetWrapper
from ulugugu.utils import cursor_over_drawing


class DebugBoundingBox(WidgetWrapper):
  def get_drawing(self):
    return drawings.DebugBoundingBox(super().get_drawing())


class MouseoverWidget(Widget):
  def __init__(self, size=(300,300)):
    self.mouseover = False
    self.timestamp = None
    self.size = size

  def value(self):
    pass

  def on_MouseMove(self, event, event_ctx):
    self.mouseover = cursor_over_drawing(self.get_drawing(), event_ctx)
    self.timestamp = time.time()
    return ACK

  def get_drawing(self):
    color = (0.2, 0.7, 0.2) if self.mouseover else (0.3, 0.5, 0.3)
    return drawings.Atop(
      drawings.Align(drawings.Text(str(self.timestamp)), (0, 1)),
      drawings.Rectangle(self.size, color)
    )

  def on_unhandled_event(self, event, event_ctx):
    pass


class ChangingSizeWidget(Widget):
  def __init__(self, initial_size=(300, 300)):
    self.size = initial_size

  def value(self):
    pass

  def on_MousePress(self, event, event_ctx):
    # Catch focus
    return ACK

  def on_KeyPress_CHAR_P(self, event_ctx):
    self.size = vec2.add(self.size, (10, 10))
    return ACK

  def on_KeyPress_CHAR_M(self, event_ctx):
    self.size = vec2.sub(self.size, (10, 10))
    return ACK

  def get_drawing(self):
    return drawings.Align(
      drawings.Atop(
        drawings.Align(drawings.Text(str(self.size)), (0.5, 0.5)),
        drawings.Align(drawings.Rectangle(self.size, (0.5, 0.3, 0.3)), (0.5, 0.5))
      ),
      (0, 0)
    )

  def on_unhandled_event(self, event, event_ctx):
    pass
