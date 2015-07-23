from ulugugu.widgets import Widget


class StaticWidget(Widget):
  def __init__(self, drawing):
    self.drawing = drawing

  def get_drawing(self):
    return self.drawing

  def value(self):
    return None

  on_KeyPress_default = Widget.ignore
  on_MousePress       = Widget.ignore
  on_MouseRelease     = Widget.ignore
  on_MouseMove        = Widget.ignore
  on_ReceiveChild     = Widget.ignore
  on_Drag             = Widget.ignore
  on_DragStart        = Widget.ignore
  on_DragStop         = Widget.ignore
