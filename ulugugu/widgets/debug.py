from ulugugu.widgets import WidgetWrapper
from ulugugu import drawings


class DebugBoundingBox(WidgetWrapper):
  def get_drawing(self):
    return drawings.DebugBoundingBox(super().get_drawing())
