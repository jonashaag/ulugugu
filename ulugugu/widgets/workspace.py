from ulugugu import drawings, keys
from ulugugu.events import ACK, KeyPress, event_used, send_event
from ulugugu.widgets import Widget, StaticWidget, Above
from ulugugu.widgets.container import Container
from ulugugu.widgets.input import StringInput, IntegerInput


class Workspace(Widget):
  def __init__(self, width, height):
    self.container = WorkspaceContainer(width, height)

  def on_unhandled_event(self, event, event_ctx):
    return send_event(self.container, event, event_ctx)

  def add_child(self, child, offset):
    self.container.add_child(child, offset)

  def value(self):
    return self._get_widget().value()[1]

  def get_drawing(self):
    return self._get_widget().get_drawing()

  def _get_widget(self):
    return Above(StaticWidget(drawings.Text(str(len(self.container.children)))), self.container)


class WorkspaceContainer(Container):
  def __init__(self, width, height):
    super().__init__()
    self._width = width
    self._height = height

  def value(self):
    pass

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
    self.add_child(StringInput("Some text"), (300, 300))
    return ACK

  def on_KeyPress_CHAR_I(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_I), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.add_child(IntegerInput(), (100, 100))
    return ACK

  def on_KeyPress_ESCAPE(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.ESCAPE), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
      else:
        self.focused_child = None
        return ACK
