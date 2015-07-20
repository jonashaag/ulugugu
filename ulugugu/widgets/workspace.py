from ulugugu import drawings, keys
from ulugugu.events import ACK, KeyPress, event_used
from ulugugu.widgets import ChangeDrawing
from ulugugu.widgets.container import Container, PositionedChild
from ulugugu.widgets.input import StringInput, IntegerInput


class Workspace(ChangeDrawing):
  def __init__(self, width, height):
    super().__init__(WorkspaceContainer(width, height))

  @property
  def children(self):
    return self.child.children

  def get_drawing(self):
    container_drawing = self.child.get_drawing()
    child_counter = drawings.Text(str(len(self.child.children)))
    return drawings.Above(child_counter, container_drawing)

  def get_child_position(self):
    drawing = self.get_drawing()
    l, t, _, _ = drawing.snd.boundingbox
    return -l, -t


class WorkspaceContainer(Container):
  def __init__(self, width, height):
    super().__init__()
    self._width = width
    self._height = height

  def value(self):
    pass

  def update_child_positions(self):
    pass

  def can_add_child(self, positioned_child):
    return True

  def get_drawing(self):
    border = drawings.Rectangle(
      (self._width, self._height),
      color=(0.7, 0.7, 0.7),
      fill='stroke'
    )
    return drawings.Atop(border, super().get_drawing()) \
              .clone(boundingbox=border.boundingbox)

  def on_KeyPress_CHAR_T(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_T), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.children.append(PositionedChild(StringInput("Some text"), (300, 300)))
    return ACK

  def on_KeyPress_CHAR_I(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_I), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.children.append(PositionedChild(IntegerInput(), (100, 100)))
    return ACK

  def on_KeyPress_ESCAPE(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.ESCAPE), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
      else:
        self.focused_child = None
        return ACK
