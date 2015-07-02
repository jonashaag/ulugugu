from ulugugu import drawings
from ulugugu.widgets import WidgetWrapper


class DebugBoundingBox(WidgetWrapper):
  def get_drawing(self):
    drawing = super().get_drawing()
    border = drawings.Rectangle(
      width=drawing.width(),
      height=drawing.height(),
      color=(0.9, 0.9, 0.9),
      fill='stroke'
    )
    return drawings.Atop(border, drawing)
